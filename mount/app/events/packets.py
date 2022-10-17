from typing import Awaitable
from typing import Callable
from uuid import UUID

from app.common import logging
from app.common import serial
from app.common.context import Context
from app.models.accounts import Account
from app.models.beatmaps import Beatmap
from app.models.chats import Chat
from app.models.members import Member
from app.models.presences import Presence
from app.models.sessions import Session
from app.models.spectators import Spectator
from app.models.stats import Stats
from app.services.beatmaps_client import BeatmapsClient
from app.services.chats_client import ChatsClient
from app.services.users_client import UsersClient

PACKET_HANDLERS = {}

PacketHandler = Callable[[Context, Session, bytes], Awaitable[bytes]]


def get_packet_handler(packet_id: int) -> PacketHandler | None:
    return PACKET_HANDLERS.get(packet_id)


async def handle_packet_event(ctx: Context, session: Session, packet_id: int,
                              packet_data: bytes) -> bytes:
    packet_handler = get_packet_handler(packet_id)
    packet_name = serial.client_packet_id_to_name(packet_id)

    if packet_handler is None:
        if packet_id != serial.ClientPackets.LOGOUT:
            response_data = serial.write_notification_packet(
                f"[Unhandled Packet] {packet_name} ({packet_id})")
        else:
            response_data = b""

        logging.warning("Unhandled packet", type=packet_name)
        return response_data

    logging.info("Handling packet", type=packet_name,
                 length=len(packet_data))

    response_data = await packet_handler(ctx, session, packet_data)
    return response_data


def packet_handler(packet_id: int) -> Callable[[PacketHandler], PacketHandler]:
    def decorator(func: PacketHandler) -> PacketHandler:
        PACKET_HANDLERS[packet_id] = func
        return func
    return decorator


@packet_handler(serial.ClientPackets.PING)
async def handle_ping(ctx: Context, session: Session,  packet_data: bytes
                      ) -> bytes:
    # NOTE: this makes osu! send it's next request immediately
    # could be useful for something like a 'low delay mode'?
    # return serial.write_pong_packet()

    return b""


@packet_handler(serial.ClientPackets.LOGOUT)
async def handle_logout(ctx: Context, session: Session, packet_data: bytes
                        ) -> bytes:
    # (?) clear user packet queue

    users_client = UsersClient(ctx)
    chats_client = ChatsClient(ctx)

    # delete user presence
    presence = await users_client.delete_presence(session.session_id)
    if presence is None:
        return b""

    # delete user session
    deleted_session = await users_client.log_out(session.session_id)
    if deleted_session is None:
        return b""

    # remove user from all chats they're in
    chats = await chats_client.get_chats()
    if chats is None:
        return b""

    for chat in chats:
        chat_left = await chats_client.leave_chat(chat.chat_id,
                                                  session.session_id)
        if chat_left is None:
            return b""

    # inform all other players that the user has logged out
    # TODO: should we be fetching the osu-specific sessions here?
    # should sessions be refactored so that we have osu-specific ones?
    data = serial.write_user_logout_packet(session.account_id)

    other_presences = await users_client.get_all_presences()
    if other_presences is None:
        return b""

    for other_presence in other_presences:
        # commented since we're already logged out.
        # left here because it's logical
        # if other_presence.session_id == session.session_id:
        #     continue

        success = await users_client.enqueue_packet(other_presence.session_id,
                                                    data=list(data))
        if not success:
            return b""

    return b""


@packet_handler(serial.ClientPackets.REQUEST_SELF_STATS)
async def handle_request_game_mode_stats(ctx: Context, session: Session,
                                         packet_data: bytes) -> bytes:
    users_client = UsersClient(ctx)

    presence = await users_client.get_presence(session.session_id)
    if presence is None:
        return b""

    stats = await users_client.get_stats(session.account_id,
                                         presence.game_mode)
    if stats is None:
        return b""

    return serial.write_user_stats_packet(
        account_id=session.account_id,
        action=presence.action,
        info_text=presence.info_text,
        map_md5=presence.map_md5,
        mods=presence.mods,
        mode=presence.game_mode,
        map_id=presence.map_id,
        ranked_score=stats.ranked_score,
        accuracy=stats.accuracy,
        play_count=stats.play_count,
        total_score=stats.total_score,
        global_rank=0,  # TODO
        pp=stats.performance,
    )


@packet_handler(serial.ClientPackets.REQUEST_ALL_USER_STATS)
async def handle_request_all_user_stats_request(ctx: Context, session: Session,
                                                packet_data: bytes) -> bytes:
    users_client = UsersClient(ctx)

    presences = await users_client.get_all_presences()
    if presences is None:
        return b""

    response_buffer = bytearray()

    for presence in presences:
        if presence.session_id == session.session_id:
            continue

        stats = await users_client.get_stats(presence.account_id,
                                             presence.game_mode)
        if stats is None:
            return b""

        response_buffer += serial.write_user_stats_packet(
            account_id=stats.account_id,
            action=presence.action,
            info_text=presence.info_text,
            map_md5=presence.map_md5,
            mods=presence.mods,
            mode=presence.game_mode,
            map_id=presence.map_id,
            ranked_score=stats.ranked_score,
            accuracy=stats.accuracy,
            play_count=stats.play_count,
            total_score=stats.total_score,
            global_rank=0,  # TODO
            pp=stats.performance,
        )

    return bytes(response_buffer)


@packet_handler(serial.ClientPackets.CHANGE_ACTION)
async def handle_change_action_request(ctx: Context, session: Session,
                                       packet_data: bytes) -> bytes:
    with memoryview(packet_data) as raw_data:
        data_reader = serial.Reader(raw_data)
        action = data_reader.read_uint8()
        info_text = data_reader.read_string()
        map_md5 = data_reader.read_string()
        mods = data_reader.read_uint32()
        mode = data_reader.read_uint8()
        # TODO: convert mode to std/rx/ap?
        # https://github.com/osuAkatsuki/bancho.py/blob/master/app/api/domains/cho.py#L188-L197
        map_id = data_reader.read_int32()

    users_client = UsersClient(ctx)

    presence = await users_client.partial_update_presence(
        session.session_id,
        action=action,
        info_text=info_text,
        map_md5=map_md5,
        mods=mods,
        game_mode=mode,
        map_id=map_id,
    )
    if presence is None:
        return b""

    stats = await users_client.get_stats(presence.account_id,
                                         presence.game_mode)
    if stats is None:
        return b""

    # broadcast the new presence to all other users
    # TODO: if the user is restricted, should not happen
    other_presences = await users_client.get_all_presences()
    if other_presences is None:
        return b""

    data = serial.write_user_stats_packet(account_id=session.account_id,
                                          action=action,
                                          info_text=info_text,
                                          map_md5=map_md5,
                                          mods=mods,
                                          mode=mode,
                                          map_id=map_id,
                                          ranked_score=stats.ranked_score,
                                          accuracy=stats.accuracy,
                                          play_count=stats.play_count,
                                          total_score=stats.total_score,
                                          global_rank=0,  # TODO
                                          pp=stats.performance)

    for other_presence in other_presences:
        success = await users_client.enqueue_packet(other_presence.session_id,
                                                    data=list(data))
        if not success:
            return b""

    return b""


@packet_handler(serial.ClientPackets.UPDATE_PRESENCE_FILTER)
async def handle_update_presence_filter_request(ctx: Context, session: Session,
                                                packet_data: bytes) -> bytes:
    with memoryview(packet_data) as raw_data:
        data_reader = serial.Reader(raw_data)
        presence_filter = data_reader.read_uint8()

    if presence_filter not in range(0, 3):
        logging.warning("User sent an invalid presence filter",
                        session_id=session.session_id,
                        presence_filter=presence_filter)
        return b""

    # TODO: set this on the user

    return b""


# these channels are client-only and don't exist on the server
# (but the osu! client will still send requests for them xd)
CLIENT_ONLY_CHANNELS = ("#hightlight", "#userlog")


@packet_handler(serial.ClientPackets.SEND_PUBLIC_MESSAGE)
async def handle_send_public_message_request(ctx: Context, session: Session,
                                             packet_data: bytes) -> bytes:
    with memoryview(packet_data) as raw_data:
        data_reader = serial.Reader(raw_data)
        sender_name = data_reader.read_string()
        message = data_reader.read_string()
        recipient_name = data_reader.read_string()
        sender_id = data_reader.read_int32()

        # TODO: not sure if these can change?
        assert sender_name == ""
        assert sender_id == 0

    message = message.strip()
    if not message:
        return b""

    if recipient_name in CLIENT_ONLY_CHANNELS:
        return b""

    if len(message) > 1000:
        logging.warning("User sent a message that was too long",
                        session_id=session.session_id,
                        message=message)
        return serial.write_notification_packet("Your message was not sent.\n"
                                                "(it exceeded the 1K character limit)")

    users_client = UsersClient(ctx)
    chats_client = ChatsClient(ctx)

    # TODO: instance channels will need to be handled differently
    chats = await chats_client.get_chats(name=recipient_name)
    if chats is None:
        return b""

    if not chats:
        logging.warning("User sent a message to a non-existent chat",
                        session_id=session.session_id,
                        recipient_name=recipient_name)
        return b""

    chat = chats[0]

    chat_members = await chats_client.get_members(chat.chat_id)
    if chat_members is None:
        return b""

    # make sure sender is actually in the chats members
    if not any(member.account_id == session.account_id
               for member in chat_members):
        logging.warning("User sent a message to a chat they are not in",
                        session_id=session.session_id,
                        chat_id=chat.chat_id, chat_name=chat.name)
        return b""

    account = await users_client.get_account(session.account_id)
    if account is None:
        return b""

    data = serial.write_send_message_packet(sender=account.username,
                                            message=message,
                                            recipient=recipient_name,
                                            sender_id=account.account_id)

    for chat_member in chat_members:
        if chat_member.session_id == session.session_id:
            continue

        success = await users_client.enqueue_packet(chat_member.session_id,
                                                    data=list(data))
        if not success:
            return b""

    return b""


@packet_handler(serial.ClientPackets.CHANNEL_PART)
async def handle_channel_part_request(ctx: Context, session: Session,
                                      packet_data: bytes) -> bytes:
    with memoryview(packet_data) as raw_data:
        data_reader = serial.Reader(raw_data)
        channel_name = data_reader.read_string()

    if channel_name in CLIENT_ONLY_CHANNELS:
        return b""

    users_client = UsersClient(ctx)
    chats_client = ChatsClient(ctx)

    chats = await chats_client.get_chats(name=channel_name)
    if chats is None:
        return b""

    if len(chats) != 1:
        # logging.error("Failed to get chat",
        #               channel_name=channel_name,
        #               session_id=session.session_id)
        return b""

    chat = chats[0]

    # check if user is already in channel
    members = await chats_client.get_members(chat.chat_id)
    if members is None:
        return b""

    for member in members:
        if member.account_id == session.account_id:
            break
    else:
        logging.error("User attempted to leave channel they're not in",
                      channel_name=channel_name,
                      session_id=session.session_id)
        return b""

    chat_left = await chats_client.leave_chat(chat.chat_id,
                                              session.session_id)
    if chat_left is None:
        return b""

    # send updated channel info (player count) to everyone that can see it
    updated_channel_info = serial.write_channel_info_packet(channel=chat.name,
                                                            topic=chat.topic,
                                                            user_count=len(members) - 1)

    presences = await users_client.get_all_presences()
    if presences is None:
        return b""

    for presence in presences:
        # TODO: only if they have read privs

        success = await users_client.enqueue_packet(presence.session_id,
                                                    list(updated_channel_info))
        if not success:
            return b""

    return b""


@packet_handler(serial.ClientPackets.START_SPECTATING)
async def handle_start_spectating_request(ctx: Context, session: Session,
                                          packet_data: bytes) -> bytes:
    with memoryview(packet_data) as raw_data:
        data_reader = serial.Reader(raw_data)
        target_id = data_reader.read_int32()

    users_client = UsersClient(ctx)

    sessions = await users_client.get_all_sessions(account_id=target_id)
    if sessions is None:
        return b""

    if len(sessions) != 1:
        logging.error("Failed to get session",
                      target_id=target_id,
                      session_id=session.session_id)
        return b""

    target_session = sessions[0]

    spectator = await users_client.create_spectator(
        host_session_id=target_session.session_id,
        session_id=session.session_id,
        account_id=session.account_id)
    if spectator is None:
        return b""

    data = serial.write_spectator_joined_packet(session.account_id)
    success = await users_client.enqueue_packet(target_session.session_id,
                                                data=list(data))
    if not success:
        return b""

    spectators = await users_client.get_spectators(target_session.session_id)
    if spectators is None:
        return b""

    response_buffer = bytearray()

    data = serial.write_fellow_spectator_joined_packet(session.account_id)
    for spectator in spectators:
        if spectator == session.session_id:
            continue

        # them to us
        response_buffer += serial.write_fellow_spectator_joined_packet(
            spectator.account_id)

        # us to them
        success = await users_client.enqueue_packet(spectator.session_id,
                                                    data=list(data))
        if not success:
            return b""

    return bytes(response_buffer)


@packet_handler(serial.ClientPackets.STOP_SPECTATING)
async def handle_stop_spectating_request(ctx: Context, session: Session,
                                         packet_data: bytes) -> bytes:
    users_client = UsersClient(ctx)

    # get the user we're spectating
    host_session_id = await users_client.get_spectator_host(session.session_id)
    if host_session_id is None:
        return b""

    # stop spectating them
    spectator = await users_client.delete_spectator(
        host_session_id=host_session_id,
        session_id=session.session_id)
    if spectator is None:
        return b""

    # tell them we stopped spectating
    data = serial.write_spectator_left_packet(session.account_id)
    success = await users_client.enqueue_packet(host_session_id,
                                                data=list(data))
    if not success:
        return b""

    # tell everyone else we stopped spectating
    spectators = await users_client.get_spectators(host_session_id)
    if spectators is None:
        return b""

    response_buffer = bytearray()

    data = serial.write_fellow_spectator_left_packet(session.account_id)
    for spectator in spectators:
        if spectator == session.session_id:
            continue

        # them to us
        response_buffer += serial.write_fellow_spectator_left_packet(
            spectator.account_id)

        # us to them
        success = await users_client.enqueue_packet(spectator.session_id,
                                                    data=list(data))
        if not success:
            return b""

    return bytes(response_buffer)


@packet_handler(serial.ClientPackets.SPECTATE_FRAMES)
async def handle_spectate_frames_request(ctx: Context, session: Session,
                                         packet_data: bytes) -> bytes:
    with memoryview(packet_data) as frame_bundle_data:
        data_reader = serial.Reader(frame_bundle_data)
        frame_bundle_data = data_reader.read_bytes()

    # TODO: validate that the data the user is sending is valid

    users_client = UsersClient(ctx)

    spectators = await users_client.get_spectators(session.session_id)
    if spectators is None:
        return b""

    data = serial.write_spectate_frames_packet(frame_bundle_data)

    for spectator in spectators:
        success = await users_client.enqueue_packet(spectator.session_id,
                                                    data=list(data))
        if not success:
            return b""

    return b""


@packet_handler(serial.ClientPackets.CHANNEL_JOIN)
async def handle_channel_join_request(ctx: Context, session: Session,
                                      packet_data: bytes) -> bytes:
    with memoryview(packet_data) as raw_data:
        data_reader = serial.Reader(raw_data)
        channel_name = data_reader.read_string()

    if channel_name in CLIENT_ONLY_CHANNELS:
        return b""

    chats_client = ChatsClient(ctx)

    chats = await chats_client.get_chats(name=channel_name)
    if chats is None:
        return b""

    if len(chats) != 1:
        # logging.error("Failed to get chat",
        #               channel_name=channel_name,
        #               session_id=session.session_id)
        return b""

    chat = chats[0]

    # https://github.com/osuAkatsuki/bancho.py/blob/25d844eb6e2b9ec89e73fcc3b4b7632dbbf35709/app/objects/player.py#L758-L790

    # check if user is already in channel
    members = await chats_client.get_members(chat.chat_id)
    if members is None:
        return b""

    for member in members:
        if member.account_id == session.account_id:
            logging.error("User attempted to join channel they're already in",
                          channel_name=channel_name,
                          session_id=session.session_id)
            return b""

    # check if user has read privileges to the channel
    # TODO

    # check if channel is #lobby; if so, only allow if we're in mp lobby?

    # join the channel
    users_client = UsersClient(ctx)

    account = await users_client.get_account(session.account_id)
    if account is None:
        return b""

    member = await chats_client.join_chat(chat.chat_id,
                                          session.session_id,
                                          session.account_id,
                                          account.username,
                                          privileges=0)  # TODO
    if member is None:
        return b""

    # TODO: attach channel to player?

    response_buffer = bytearray()

    response_buffer += serial.write_channel_join_success_packet(channel_name)

    # send updated channel info (player count) to everyone that can see it
    updated_channel_info = serial.write_channel_info_packet(channel=chat.name,
                                                            topic=chat.topic,
                                                            user_count=len(members) + 1)

    presences = await users_client.get_all_presences()
    if presences is None:
        return b""

    for presence in presences:
        # TODO: only if they have read privs

        success = await users_client.enqueue_packet(presence.session_id,
                                                    list(updated_channel_info))
        if not success:
            return b""

    return bytes(response_buffer)
