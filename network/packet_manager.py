from .packet_parser import PacketParser, PacketType
from .network_exceptions import ErrorPacketError


class PacketManager(object):

    def __init__(self, network_manager):
        self.packet_parser = PacketParser()
        self.network_manager = network_manager
        print("Created packet manager")

    def start(self):
        self.network_manager.start()

    def stop(self):
        try:
            self.send_raw([], PacketType.CLOSE_CONNECTION_PACKET)
        finally:
            self.network_manager.stop()

    def get_packet_name(self, packet):
        return self.packet_parser.get_packet_name(packet)

    def get_packet_name_by_type(self, p_type):
        return self.packet_parser.get_packet_name_by_type(p_type)

    def create_packet(self, packet_data, packet_type):
        return self.packet_parser.create_packet(packet_data, packet_type)

    def send_raw(self, packet_data, packet_type):
        packet = self.packet_parser.create_packet(packet_data, packet_type)
        self.network_manager.send(packet)

    def send_packet(self, packet):
        self.network_manager.send(packet)

    def read_packet(self, timeout=None):
        """
        If timeout specified then could raise NetworkTimeoutError

        Anyway raises BrokenPacketError and HardwareError
        """
        packet = self.packet_parser.\
            parse(self.network_manager.read(timeout=timeout))

        if packet["type"] == PacketType.ERROR_PACKET:
            raise ErrorPacketError(str(packet["data"]))

        return packet
