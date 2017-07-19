import socket
import logging
import network.network_exceptions as net_ex

DEFAULT_PORT = 1098
BROADCAST_ADDR = '255.255.255.255'
BROADCAST_PORT = 1094
LISTEN_HOST = ''
LISTEN_TIMEOUT = 1
OBSERVER_CONTROL_BYTE = 0xAD
OBSERVER_VALIDATION_BYTE = 0xFF
OBSERVER_RUNNING = 1
OBSERVER_STOPPED = 2

HEADER_SIZE = 1
PORT_SIZE = 4
KEY_SIZE = 32

OBSERVER_PACKET_SIZE = KEY_SIZE + PORT_SIZE + HEADER_SIZE

DEFAULT_KEY = "00000000000000000000000000000000"

RETRIES = 5

network_logger = logging.getLogger("network_logger")


def observe(self, key=DEFAULT_KEY, port=DEFAULT_PORT):
    listen_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    listen_sock.settimeout(LISTEN_TIMEOUT)
    listen_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    listen_sock.bind((LISTEN_HOST, port))

    address = None
    for i in range(RETRIES):
        send_broadcast(port, key)

        try:
            network_logger.debug("Trying to connect...")
            data, address = listen_sock.recvfrom(1)
            data = bytearray(data)
            network_logger.debug("Get answer")

            if data.__len__() != 0:
                listen_sock.close()
                byte = int(data[0])

                if byte == OBSERVER_VALIDATION_BYTE:
                    network_logger.debug("Found validation byte")
                    break
                else:
                    raise net_ex.NetworkConnectionError("Wrong validation "
                                                        "byte from ESP")

        except socket.timeout:
            pass

    if not address:
        raise net_ex.NetworkConnectionError("Can't establish "
                                            "connection with ESP")

    return address[0]


def send_broadcast(port, key):
    broadcast_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    broadcast_sock.settimeout(0.25)
    broadcast_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    # Create data array
    obs_data = bytearray()
    obs_data.append(OBSERVER_CONTROL_BYTE)

    # Add key information
    for c in key:
        obs_data.append(ord(c))

    # Add port information
    port = int_to_bytes(port)
    for byte in port:
        obs_data.append(byte)

    # Send broadcast message
    broadcast_sock.sendto(obs_data, 0, (BROADCAST_ADDR, BROADCAST_PORT))
    broadcast_sock.close()


def int_to_bytes(integer):
    res = bytearray()
    bytes_of_int = [((integer >> i) & 0xFF) for i in (24, 16, 8, 0)]
    for i in bytes_of_int:
        res.append(i)
    return res
