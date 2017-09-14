from . import programmer_exceptions as ex
from network import protocol as pl


class PacketType(object):

    PROG_INIT_PACKET = 1
    STOP_PACKET = 2
    CMD_PACKET = 3
    RESET_PACKET = 4
    PROG_MEM_PACKET = 5
    USART_CONF_PACKET = 6
    USART_PACKET = 7
    ACK_PACKET = 8
    AVR_PROG_INIT_PACKET = 9
    READ_MEM_PACKET = 10
    MEMORY_PACKET = 11
    LOAD_NETWORK_INFO_PACKET = 12
    LOAD_MCU_INFO_PACKET = 13


class PacketError(object):

    INTERNAL_ERROR = 1
    WRONG_PACKET = 2


class PacketParser(object):

        def __init__(self):
            self.packets_names = dict()
            self.__create_packet_names_dict()

        # ###########################################
        #   Create packet
        #
        #############################################
        def parse(self, raw_packet):
            if len(raw_packet) < pl.PL_PACKET_HEADER_SIZE:
                raise ex.BrokenPacketError("Wrong packet length: "
                                           "less than packet header size")

            data_offset = pl.PL_PACKET_HEADER_SIZE

            # No CRC32 on CC3200
            # if not self.check_crc(raw_packet):
            #    raise ex.BrokenPacketError("CRC doesn't match.")

            data_len = len(raw_packet) - pl.PL_RESERVED_BYTES
            packet_type = self.get_type(raw_packet[pl.PL_TYPE_FIELD_OFFSET])

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
        def create_packet(self, data, packet_type, comp=False, enc=False,
                          sign=False):

            packet_len = len(data) + pl.PL_RESERVED_BYTES

            if packet_len > pl.PL_MAX_DATA_LENGTH:
                raise ex.BrokenPacketError("Packet is too large "
                                           "when trying to create "
                                           "packet")

            packet = bytearray()
            packet.append(pl.PL_START_FRAME_BYTE)
            packet.append(self._get_flag_byte(comp, enc, sign))
            packet.append(self._get_packet_byte(packet_type))
            packet.extend([(packet_len >> 8) & 0xFF, (packet_len & 0xFF)])
            packet.extend(data)

            # No CRC32 on CC3200 since UART connection in the absence of
            #   UART connection
            #
            # crc = self.crc32.crc32_stm(packet)
            # packet.extend([(crc >> 24) & 0xFF, (crc >> 16) & 0xFF,
            #               (crc >> 8) & 0xFF, crc & 0xFF])

            return packet

        def get_type(self, type_byte):
            if type_byte == pl.PL_PROG_INIT_PACKET_BYTE:
                return PacketType.PROG_INIT_PACKET

            elif type_byte == pl.PL_STOP_PACKET_BYTE:
                return PacketType.STOP_PACKET

            elif type_byte == pl.PL_CMD_PACKET_BYTE:
                return PacketType.CMD_PACKET

            elif type_byte == pl.PL_RESET_PACKET_BYTE:
                return PacketType.RESET_PACKET

            elif type_byte == pl.PL_PROG_MEM_PACKET_BYTE:
                return PacketType.PROG_MEM_PACKET

            elif type_byte == pl.PL_USART_CONF_PACKET_BYTE:
                return PacketType.USART_CONF_PACKET

            elif type_byte == pl.PL_USART_PACKET_BYTE:
                return PacketType.USART_PACKET

            elif type_byte == pl.PL_ERROR_PACKET_BYTE:
                return PacketType.ERROR_PACKET

            elif type_byte == pl.PL_ACK_PACKET_BYTE:
                return PacketType.ACK_PACKET

            elif type_byte == pl.PL_AVR_PROG_INIT_PACKET_BYTE:
                return PacketType.AVR_PROG_INIT_PACKET

            elif type_byte == pl.PL_READ_MEM_PACKET_BYTE:
                return PacketType.READ_MEM_PACKET

            elif type_byte == pl.PL_MEMORY_PACKET_BYTE:
                return PacketType.MEMORY_PACKET

            elif type_byte == pl.PL_AVR_PGM_ENABLE_BYTE:
                return PacketType.AVR_PGM_ENABLE_PACKET

            elif type_byte == pl.PL_LOAD_NETWORK_INFO_BYTE:
                return PacketType.LOAD_NETWORK_INFO_PACKET

            else:
                raise ex.BrokenPacketError("Unknown packet type")

        def _get_packet_byte(self, _type):

            if _type == PacketType.PROG_INIT_PACKET:
                return pl.PL_PROGRAMMER_INIT

            elif _type == PacketType.STOP_PACKET:
                return pl.PL_PROGRAMMER_STOP

            elif _type == PacketType.CMD_PACKET:
                return pl.PL_CMD

            elif _type == PacketType.RESET_PACKET:
                return pl.PL_RESET

            elif _type == PacketType.PROG_MEM_PACKET:
                return pl.PL_PROGRAM_MEMORY

            elif _type == PacketType.USART_CONF_PACKET:
                return pl.PL_UART_CONFIGURATION

            elif _type == PacketType.USART_PACKET:
                return pl.PL_UART_DATA

            elif _type == PacketType.ACK_PACKET:
                return pl.PL_ACK

            elif _type == PacketType.READ_MEM_PACKET:
                return pl.PL_READ_MEMORY

            elif _type == PacketType.MEMORY_PACKET:
                return pl.PL_MEMORY

            elif _type == PacketType.LOAD_MCU_INFO_PACKET:
                return pl.PL_LOAD_MCU_INFO

            elif _type == PacketType.LOAD_NETWORK_INFO_PACKET:
                return pl.PL_LOAD_NETWORK_INFO_BYTE

            else:
                raise ex.BrokenPacketError("Unknown packet type")

        def get_error_byte(self, error):
            if error == PacketError.INTERNAL_ERROR:
                return pl.PL_INTERNAL_ERROR_BYTE

            elif error == PacketError.WRONG_PACKET:
                return pl.PL_WRONG_PACKET_ERROR_BYTE

            else:
                raise ex.BrokenPacketError("Unknown error type")

        def get_error_type(self, error_byte):

            if error_byte == pl.PL_INTERNAL_ERROR_BYTE:
                return PacketError.INTERNAL_ERROR

            elif error_byte == pl.PL_WRONG_PACKET_ERROR_BYTE:
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

        def __get_flag_bit(self, b, flag):
            return ((b >> flag) & 0x01)

        def __set_flag_bit(self, b, flag):
            return (b | (1 << flag))

        def _get_flag_byte(self, comp, enc, sign):
            b = 0

            if comp:
                b = self.__set_flag_bit(b, pl.PL_FLAG_COMPRESSION_BIT)

            if enc:
                b = self.__set_flag_bit(b, pl.PL_FLAG_ENCRYPTION_BIT)

            if sign:
                b = self.__set_flag_bit(b, pl.PL_FLAG_SIGN_BIT)

            return b

        def check_crc(self, data):
            crc_data = data[0:len(data)-self.CRC_FIELD_SIZE]
            crc = self.crc32.crc32_stm(crc_data)

            crc_true = 0
            for i in range(self.CRC_FIELD_SIZE):
                crc_true |= (int(data[len(data)-(i+1)]) << 8*i)

            if crc == crc_true:
                return True

            return False

        def __create_packet_names_dict(self):
            self.packets_names[PacketType.PROG_INIT_PACKET] = "ProgInitPacket"
            self.packets_names[PacketType.STOP_PACKET] = "StopPacket"
            self.packets_names[PacketType.CMD_PACKET] = "CmdPacket"
            self.packets_names[PacketType.RESET_PACKET] = "ResetPacket"
            self.packets_names[PacketType.PROG_MEM_PACKET] = "ProgMemPacket"
            self.packets_names[PacketType.USART_CONF_PACKET] = "UsartConfPacket"
            self.packets_names[PacketType.USART_PACKET] = "UsartPacket"
            self.packets_names[PacketType.ACK_PACKET] = "AckPacket"
            self.packets_names[PacketType.AVR_PROG_INIT_PACKET] =\
                "AvrProgInitPacket"
            self.packets_names[PacketType.READ_MEM_PACKET] = "AvrReadMemPacket"
            self.packets_names[PacketType.MEMORY_PACKET] = "MemoryPacket"
            self.packets_names[PacketType.LOAD_MCU_INFO_PACKET] =\
                "LoadMcuInfoPacket"
