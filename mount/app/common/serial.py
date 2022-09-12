from __future__ import annotations

import struct

# writing


def pack_uint8(value: int) -> bytes:
    return struct.pack('<B', value)


def pack_uint16(value: int) -> bytes:
    return struct.pack('<H', value)


def pack_uint32(value: int) -> bytes:
    return struct.pack('<I', value)


def pack_uint64(value: int) -> bytes:
    return struct.pack('<Q', value)


def pack_int8(value: int) -> bytes:
    return struct.pack('<b', value)


def pack_int16(value: int) -> bytes:
    return struct.pack('<h', value)


def pack_int32(value: int) -> bytes:
    return struct.pack('<i', value)


def pack_int64(value: int) -> bytes:
    return struct.pack('<q', value)


def pack_float(value: float) -> bytes:
    return struct.pack('<f', value)


def pack_double(value: float) -> bytes:
    return struct.pack('<d', value)


# copilot version i might use later
# def pack_string(value: str) -> bytes:
#     # uleb128
#     buffer = bytearray()
#     value2 = value.encode('utf-8')
#     length = len(value2)
#     while length >= 0x80:
#         buffer.append((length & 0x7F) | 0x80)
#         length >>= 7
#     buffer.append(length)
#     buffer.extend(value2)
#     return buffer


def pack_string(value: str) -> bytes:
    if not value:
        return b"\x00"

    encoded = value.encode('utf-8')
    bytes_remaining = len(encoded)

    ret = bytearray()
    ret += b"\x0b"

    while bytes_remaining > 0:
        ret.append(bytes_remaining & 0x7F)
        bytes_remaining >>= 7
        if bytes_remaining > 0:
            ret[-1] |= 0x80

    ret.extend(encoded)
    return ret


# reading

class Reader:
    def __init__(self, data: bytes):
        # TODO: memoryview instead of (data, offset)?
        self.data = data
        self.offset = 0

    def read_uint8(self) -> int:
        value = struct.unpack_from('<B', self.data, self.offset)[0]
        self.offset += 1
        return value

    def read_uint16(self) -> int:
        value = struct.unpack_from('<H', self.data, self.offset)[0]
        self.offset += 2
        return value

    def read_uint32(self) -> int:
        value = struct.unpack_from('<I', self.data, self.offset)[0]
        self.offset += 4
        return value

    def read_uint64(self) -> int:
        value = struct.unpack_from('<Q', self.data, self.offset)[0]
        self.offset += 8
        return value

    def read_int8(self) -> int:
        value = struct.unpack_from('<b', self.data, self.offset)[0]
        self.offset += 1
        return value

    def read_int16(self) -> int:
        value = struct.unpack_from('<h', self.data, self.offset)[0]
        self.offset += 2
        return value

    def read_int32(self) -> int:
        value = struct.unpack_from('<i', self.data, self.offset)[0]
        self.offset += 4
        return value

    def read_int64(self) -> int:
        value = struct.unpack_from('<q', self.data, self.offset)[0]
        self.offset += 8
        return value

    def read_float(self) -> float:
        value = struct.unpack_from('<f', self.data, self.offset)[0]
        self.offset += 4
        return value

    def read_double(self) -> float:
        value = struct.unpack_from('<d', self.data, self.offset)[0]
        self.offset += 8
        return value

    def read_string(self) -> str:
        length = 0
        shift = 0
        while True:
            byte = self.read_uint8()
            length |= (byte & 0x7F) << shift
            shift += 7
            if not byte & 0x80:
                break

        value = self.data[self.offset:self.offset + length].decode('utf-8')
        self.offset += length
        return value


# osu! packets

class ClientPackets:
    CHANGE_ACTION = 0
    SEND_PUBLIC_MESSAGE = 1
    LOGOUT = 2
    REQUEST_STATUS_UPDATE = 3
    PING = 4
    START_SPECTATING = 16
    STOP_SPECTATING = 17
    SPECTATE_FRAMES = 18
    ERROR_REPORT = 20
    CANT_SPECTATE = 21
    SEND_PRIVATE_MESSAGE = 25
    PART_LOBBY = 29
    JOIN_LOBBY = 30
    CREATE_MATCH = 31
    JOIN_MATCH = 32
    PART_MATCH = 33
    MATCH_CHANGE_SLOT = 38
    MATCH_READY = 39
    MATCH_LOCK = 40
    MATCH_CHANGE_SETTINGS = 41
    MATCH_START = 44
    MATCH_SCORE_UPDATE = 47
    MATCH_COMPLETE = 49
    MATCH_CHANGE_MODS = 51
    MATCH_LOAD_COMPLETE = 52
    MATCH_NO_BEATMAP = 54
    MATCH_NOT_READY = 55
    MATCH_FAILED = 56
    MATCH_HAS_BEATMAP = 59
    MATCH_SKIP_REQUEST = 60
    CHANNEL_JOIN = 63
    BEATMAP_INFO_REQUEST = 68
    MATCH_TRANSFER_HOST = 70
    FRIEND_ADD = 73
    FRIEND_REMOVE = 74
    MATCH_CHANGE_TEAM = 77
    CHANNEL_PART = 78
    RECEIVE_UPDATES = 79
    SET_AWAY_MESSAGE = 82
    IRC_ONLY = 84
    USER_STATS_REQUEST = 85
    MATCH_INVITE = 87
    MATCH_CHANGE_PASSWORD = 90
    TOURNAMENT_MATCH_INFO_REQUEST = 93
    USER_PRESENCE_REQUEST = 97
    USER_PRESENCE_REQUEST_ALL = 98
    TOGGLE_BLOCK_NON_FRIEND_DMS = 99
    TOURNAMENT_JOIN_MATCH_CHANNEL = 108
    TOURNAMENT_LEAVE_MATCH_CHANNEL = 109


class ServerPackets:
    ACCOUNT_ID = 5
    SEND_MESSAGE = 7
    PONG = 8
    HANDLE_IRC_CHANGE_USERNAME = 9  # unused
    HANDLE_IRC_QUIT = 10
    USER_STATS = 11
    USER_LOGOUT = 12
    SPECTATOR_JOINED = 13
    SPECTATOR_LEFT = 14
    SPECTATE_FRAMES = 15
    VERSION_UPDATE = 19
    SPECTATOR_CANT_SPECTATE = 22
    GET_ATTENTION = 23
    NOTIFICATION = 24
    UPDATE_MATCH = 26
    NEW_MATCH = 27
    DISPOSE_MATCH = 28
    TOGGLE_BLOCK_NON_FRIEND_DMS = 34
    MATCH_JOIN_SUCCESS = 36
    MATCH_JOIN_FAIL = 37
    FELLOW_SPECTATOR_JOINED = 42
    FELLOW_SPECTATOR_LEFT = 43
    ALL_PLAYERS_LOADED = 45
    MATCH_START = 46
    MATCH_SCORE_UPDATE = 48
    MATCH_TRANSFER_HOST = 50
    MATCH_ALL_PLAYERS_LOADED = 53
    MATCH_PLAYER_FAILED = 57
    MATCH_COMPLETE = 58
    MATCH_SKIP = 61
    UNAUTHORIZED = 62  # unused
    CHANNEL_JOIN_SUCCESS = 64
    CHANNEL_INFO = 65
    CHANNEL_KICK = 66
    CHANNEL_AUTO_JOIN = 67
    BEATMAP_INFO_REPLY = 69
    PRIVILEGES = 71
    FRIENDS_LIST = 72
    PROTOCOL_VERSION = 75
    MAIN_MENU_ICON = 76
    MONITOR = 80  # unused
    MATCH_PLAYER_SKIPPED = 81
    USER_PRESENCE = 83
    RESTART = 86
    MATCH_INVITE = 88
    CHANNEL_INFO_END = 89
    MATCH_CHANGE_PASSWORD = 91
    SILENCE_END = 92
    USER_SILENCED = 94
    USER_PRESENCE_SINGLE = 95
    USER_PRESENCE_BUNDLE = 96
    USER_DM_BLOCKED = 100
    TARGET_IS_SILENCED = 101
    VERSION_UPDATE_FORCED = 102
    SWITCH_SERVER = 103
    ACCOUNT_RESTRICTED = 104
    RTX = 105  # unused
    MATCH_ABORT = 106
    SWITCH_TOURNAMENT_SERVER = 107


RESERVED_BYTE = b"\x00"


def write_packet(packet_id: int, data: bytes = b"") -> bytes:
    return pack_uint16(packet_id) + RESERVED_BYTE + pack_uint32(len(data)) + data


# osu! packets

def write_account_id_packet(id: int) -> bytes:
    data = pack_int32(id)
    return write_packet(ServerPackets.ACCOUNT_ID, data)


def write_send_message_packet(sender: str, message: str, recipient: str, sender_id: int) -> bytes:
    data = pack_string(sender) + pack_string(message) + \
        pack_string(recipient) + pack_int32(sender_id)
    return write_packet(ServerPackets.SEND_MESSAGE, data)


def write_pong_packet() -> bytes:
    return write_packet(ServerPackets.PONG)


def write_protocol_version_packet(version: int) -> bytes:
    data = pack_int32(version)
    return write_packet(ServerPackets.PROTOCOL_VERSION, data)


def write_privileges_packet(privileges: int) -> bytes:
    data = pack_int32(privileges)
    return write_packet(ServerPackets.PRIVILEGES, data)


def write_channel_info_packet(channel: str, topic: str, player_count: int) -> bytes:
    data = pack_string(channel) + pack_string(topic) + \
        pack_uint16(player_count)
    return write_packet(ServerPackets.CHANNEL_INFO, data)


def write_channel_info_end_packet() -> bytes:
    return write_packet(ServerPackets.CHANNEL_INFO_END)


def write_main_menu_icon_packet(icon_url: str, onclick_url: str) -> bytes:
    data = pack_string(icon_url + "|" + onclick_url)
    return write_packet(ServerPackets.MAIN_MENU_ICON, data)


def write_friends_list_packet(friends: list[int]) -> bytes:
    data = pack_uint16(len(friends))
    for friend in friends:
        data += pack_uint32(friend)
    return write_packet(ServerPackets.FRIENDS_LIST, data)


def write_silence_end_packet(remaining_sec: int) -> bytes:
    data = pack_int32(remaining_sec)
    return write_packet(ServerPackets.SILENCE_END, data)


def write_user_stats_packet(user_id: int,
                            action: int,
                            info_text: str,
                            map_md5: str,
                            mods: int,
                            mode: int,
                            map_id: int,
                            ranked_score: int,
                            accuracy: float,
                            plays: int,
                            total_score: int,
                            global_rank: int,
                            pp: int) -> bytes:
    data = (
        pack_int32(user_id)
        + pack_uint8(action)
        + pack_string(info_text)
        + pack_string(map_md5)
        + pack_int32(mods)
        + pack_uint8(mode)
        + pack_int32(map_id)
        + pack_int64(ranked_score)
        + pack_float(accuracy)
        + pack_int32(plays)
        + pack_int64(total_score)
        + pack_int32(global_rank)
        + pack_int16(pp))
    return write_packet(ServerPackets.USER_STATS, data)


def write_user_presence_packet(user_id: int,
                               username: str,
                               utc_offset: int,
                               country_code: int,
                               bancho_privileges: int,
                               mode: int,
                               latitude: float,
                               longitude: float,
                               global_rank: int) -> bytes:
    data = (
        pack_int32(user_id)
        + pack_string(username)
        + pack_uint8(utc_offset + 24)
        + pack_uint8(country_code)
        + pack_uint8(bancho_privileges | (mode << 5))
        + pack_float(latitude)
        + pack_float(longitude)
        + pack_int32(global_rank))
    return write_packet(ServerPackets.USER_PRESENCE, data)
