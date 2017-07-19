from . import programmer_exceptions as ex
from .crc32 import CRC32


class PacketType(object):

    PROG_INIT_PACKET = 1
    STOP_PACKET = 2
    CMD_PACKET = 3
    RESET_PACKET = 4
    PROG_MEM_PACKET = 5
    USART_CONF_PACKET = 6
    USART_PACKET = 7
    ERROR_PACKET = 8
    ACK_PACKET = 9
    AVR_PROG_INIT_PACKET = 10
    READ_MEM_PACKET = 11
    MEMORY_PACKET = 12
    AVR_PGM_ENABLE_PACKET = 13
    LOAD_NETWORK_INFO_PACKET = 14


class PacketError(object):

    INTERNAL_ERROR = 1
    WRONG_PACKET = 2


class PacketParser(object):

        # #######################################
        #   Packets to send + CMD packet
        #   See PacketManager.h
        # #######################################
        PROG_INIT_PACKET_BYTE = 0x11
        STOP_PACKET_BYTE = 0x22
        CMD_PACKET_BYTE = 0x33
        RESET_PACKET_BYTE = 0x44
        PROG_MEM_PACKET_BYTE = 0x55
        USART_CONF_PACKET_BYTE = 0x66
        AVR_PROG_INIT_PACKET_BYTE = 0x77
        READ_MEM_PACKET_BYTE = 0x88
        AVR_PGM_ENABLE_BYTE = 0x99
        LOAD_NETWORK_INFO_BYTE = 0x12

        # ######################################
        #   Errors
        #
        # ######################################
        INTERNAL_ERROR_BYTE = 0x00
        WRONG_PACKET_ERROR_BYTE = 0x01

        # #####################################
        #   Packet to receive + CMD packet
        #   See PacketManager.h
        # #####################################
        ACK_PACKET_BYTE = 0xAA
        USART_PACKET_BYTE = 0xBB
        ERROR_PACKET_BYTE = 0xEE
        MEMORY_PACKET_BYTE = 0xCC

        MAX_PACKET_SIZE = 300
        SIZE_FIELD_SIZE = 2
        TYPE_FIELD_SIZE = 1
        CRC_FIELD_SIZE = 4

        def __init__(self):

            self.reserved_bytes = self.SIZE_FIELD_SIZE + self.TYPE_FIELD_SIZE +\
                self.CRC_FIELD_SIZE

            self.crc32 = CRC32()

            self.packets_names = dict()
            self.packets_names[PacketType.PROG_INIT_PACKET] = "ProgInitPacket"
            self.packets_names[PacketType.STOP_PACKET] = "StopPacket"
            self.packets_names[PacketType.CMD_PACKET] = "CmdPacket"
            self.packets_names[PacketType.RESET_PACKET] = "ResetPacket"
            self.packets_names[PacketType.PROG_MEM_PACKET] = "ProgMemPacket"
            self.packets_names[PacketType.USART_CONF_PACKET] = "UsartConfPacket"
            self.packets_names[PacketType.USART_PACKET] = "UsartPacket"
            self.packets_names[PacketType.ERROR_PACKET] = "ErrorPacket"
            self.packets_names[PacketType.ACK_PACKET] = "AckPacket"
            self.packets_names[PacketType.AVR_PROG_INIT_PACKET] =\
                "AvrProgInitPacket"
            self.packets_names[PacketType.READ_MEM_PACKET] = "AvrReadMemPacket"
            self.packets_names[PacketType.MEMORY_PACKET] = "MemoryPacket"
            self.packets_names[PacketType.AVR_PGM_ENABLE_PACKET] =\
                "AvrPgmEnablePacket"

        # ###########################################
        #   Create packet
        #
        #############################################
        def parse(self, raw_packet):

            if len(raw_packet) < 3:
                raise ex.BrokenPacketError("Wrong packet length "
                                           "in PacketManager "
                                           "parse. Less than 3")

            type_offset = self.SIZE_FIELD_SIZE
            data_offset = self.SIZE_FIELD_SIZE + self.TYPE_FIELD_SIZE

            if not self.check_crc(raw_packet):
                raise ex.BrokenPacketError("CRC doesn't match.")

            data_len = len(raw_packet) - self.reserved_bytes
            packet_type = self.get_type(raw_packet[type_offset])

            if data_len == 0:
                packet = {"type": packet_type, "data_length": 0, "data": None}
            else:
                packet = {"type": packet_type,
                          "data_length": data_len,
                          "data": []}

                packet["data"].extend(raw_packet[data_offset:
                                                 data_offset+data_len])

                # print("PacketManager parse: " + str(packet["type"]) + " " +
                #      str(["0x%02x" % x for x in packet["data"]]))

            return packet

        # ##############################################
        #   Create packet to send
        #   Returns bytearray contained packet
        # ##############################################
        def create_packet(self, data, packet_type):

            packet_len = len(data) + self.reserved_bytes

            if packet_len > self.MAX_PACKET_SIZE:
                raise ex.BrokenPacketError("Packet is too large "
                                           "when trying to create "
                                           "packet")

            packet = bytearray()
            packet.extend([((packet_len >> 8) & 0xFF), (packet_len & 0xFF),
                           self.get_packet_byte(packet_type)])
            packet.extend(data)

            crc = self.crc32.crc32_stm(packet)
            packet.extend([(crc >> 24) & 0xFF, (crc >> 16) & 0xFF,
                           (crc >> 8) & 0xFF, crc & 0xFF])

            return packet

        def get_type(self, type_byte):
            if type_byte == self.PROG_INIT_PACKET_BYTE:
                return PacketType.PROG_INIT_PACKET

            elif type_byte == self.STOP_PACKET_BYTE:
                return PacketType.STOP_PACKET

            elif type_byte == self.CMD_PACKET_BYTE:
                return PacketType.CMD_PACKET

            elif type_byte == self.RESET_PACKET_BYTE:
                return PacketType.RESET_PACKET

            elif type_byte == self.PROG_MEM_PACKET_BYTE:
                return PacketType.PROG_MEM_PACKET

            elif type_byte == self.USART_CONF_PACKET_BYTE:
                return PacketType.USART_CONF_PACKET

            elif type_byte == self.USART_PACKET_BYTE:
                return PacketType.USART_PACKET

            elif type_byte == self.ERROR_PACKET_BYTE:
                return PacketType.ERROR_PACKET

            elif type_byte == self.ACK_PACKET_BYTE:
                return PacketType.ACK_PACKET

            elif type_byte == self.AVR_PROG_INIT_PACKET_BYTE:
                return PacketType.AVR_PROG_INIT_PACKET

            elif type_byte == self.READ_MEM_PACKET_BYTE:
                return PacketType.READ_MEM_PACKET

            elif type_byte == self.MEMORY_PACKET_BYTE:
                return PacketType.MEMORY_PACKET

            elif type_byte == self.AVR_PGM_ENABLE_BYTE:
                return PacketType.AVR_PGM_ENABLE_PACKET

            elif type_byte == self.LOAD_NETWORK_INFO_BYTE:
                return PacketType.LOAD_NETWORK_INFO_PACKET

            else:
                raise ex.BrokenPacketError("Unknown packet type")

        def get_packet_byte(self, _type):
            if _type == PacketType.PROG_INIT_PACKET:
                return self.PROG_INIT_PACKET_BYTE

            elif _type == PacketType.STOP_PACKET:
                return self.STOP_PACKET_BYTE

            elif _type == PacketType.CMD_PACKET:
                return self.CMD_PACKET_BYTE

            elif _type == PacketType.RESET_PACKET:
                return self.RESET_PACKET_BYTE

            elif _type == PacketType.PROG_MEM_PACKET:
                return self.PROG_MEM_PACKET_BYTE

            elif _type == PacketType.USART_CONF_PACKET:
                return self.USART_CONF_PACKET_BYTE

            elif _type == PacketType.USART_PACKET:
                return self.USART_PACKET_BYTE

            elif _type == PacketType.ERROR_PACKET:
                return self.ERROR_PACKET_BYTE

            elif _type == PacketType.ACK_PACKET:
                return self.ACK_PACKET_BYTE

            elif _type == PacketType.AVR_PROG_INIT_PACKET:
                return self.AVR_PROG_INIT_PACKET_BYTE

            elif _type == PacketType.READ_MEM_PACKET:
                return self.READ_MEM_PACKET_BYTE

            elif _type == PacketType.MEMORY_PACKET:
                return self.MEMORY_PACKET_BYTE

            elif _type == PacketType.AVR_PGM_ENABLE_PACKET:
                return self.AVR_PGM_ENABLE_BYTE

            elif _type == PacketType.LOAD_NETWORK_INFO_PACKET:
                return self.LOAD_NETWORK_INFO_BYTE

            else:
                raise ex.BrokenPacketError("Unknown packet type")

        def get_error_byte(self, error):
            if error == PacketError.INTERNAL_ERROR:
                return self.INTERNAL_ERROR_BYTE

            elif error == PacketError.WRONG_PACKET:
                return self.WRONG_PACKET_ERROR_BYTE

            else:
                raise ex.BrokenPacketError("Unknown error type")

        def get_error_type(self, error_byte):

            if error_byte == self.INTERNAL_ERROR_BYTE:
                return PacketError.INTERNAL_ERROR

            elif error_byte == self.WRONG_PACKET_ERROR_BYTE:
                return PacketError.WRONG_PACKET

            else:
                raise ex.BrokenPacketError("Unknown error byte")

        def get_packet_name(self, packet):
            packet_name = self.packets_names.get(packet["type"])

            if packet_name is None:
                raise ex.BrokenPacketError("Wrong packet type " +
                                           str(packet["type"]))

            return packet_name

        def get_packet_name_by_type(self, p_type):
            packet_name = self.packets_names.get(p_type)

            if packet_name is None:
                raise ex.BrokenPacketError("Wrong packet type " +
                                           str(p_type))

            return packet_name

        def check_crc(self, data):

            crc_data = data[0:len(data)-self.CRC_FIELD_SIZE]
            crc = self.crc32.crc32_stm(crc_data)

            crc_true = 0
            for i in range(self.CRC_FIELD_SIZE):
                crc_true |= (int(data[len(data)-(i+1)]) << 8*i)

            if crc == crc_true:
                return True

            return False
