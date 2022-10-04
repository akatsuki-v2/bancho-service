from typing import Callable
from typing import TypeVar

from app.common import logging
from app.common import serial

PACKET_HANDLERS = {}


def handle_packet_event(packet_id: int, packet_data: bytes) -> bytes:
    packet_handler = PACKET_HANDLERS.get(packet_id)
    packet_name = serial.client_packet_id_to_name(packet_id)

    if packet_handler is None:
        logging.warning("Unhandled packet", type=packet_name)
        return b""

    logging.info("Handling packet", type=packet_name, length=len(packet_data))
    response_data = packet_handler(packet_data)

    return response_data


PacketHandler = TypeVar("PacketHandler", bound=Callable[[bytes], bytes])


def packet_handler(packet_id: int) -> Callable[[PacketHandler], PacketHandler]:
    def decorator(func: PacketHandler) -> PacketHandler:
        PACKET_HANDLERS[packet_id] = func
        return func
    return decorator


@packet_handler(serial.ClientPackets.PING)
def handle_ping(packet_data: bytes) -> bytes:
    return serial.write_pong_packet()
