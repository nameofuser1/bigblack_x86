from .TCPReceiver import TCPReceiver
import socket

import logging


class NetworkManager(object):

    def __init__(self, esp_addr):
        self.esp_addr = esp_addr
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.receiver = None

        self.network_logger = logging.getLogger("network_logger")

    def start(self):
        self.sock.connect(self.esp_addr)
        self.start_listener()

    def stop(self):
        try:
            self.send_raw([], PacketType.CLOSE_CONNECTION_PACKET)
        finally:
            self.stop_listener()
            self.sock.close()

    def start_listener(self):
        if self.receiver is None:
            self.network_logger.debug("Starting receiver")
            self.receiver = TCPReceiver(self.sock)
            self.receiver.start()

    def stop_listener(self):
        if self.receiver is not None:
            self.receiver.stop()
            self.receiver = None

    def available(self):
        return self.receiver.available()

    def read(self, timeout=None):
        """
        Raises NetworkTimeoutError if timeour is expired
        """
        packet = self.receiver.read(timeout=timeout)
        self.network_logger.info("Read: " +
                                 "".join("0x%02x " % b for b in packet))

        return packet

    def send(self, packet):
        if isinstance(packet, bytearray):
            while True:
                try:
                    self.sock.send(packet)
                    self.network_logger.info("Sent: " +
                                             "".join('0x%02x ' % b
                                                     for b in packet))
                    break
                except socket.timeout:
                    pass
        else:
            raise ValueError("Packet is not bytearray")
