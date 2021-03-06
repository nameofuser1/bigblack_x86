from . import network_exceptions as ex
from network import protocol as pl


class PacketType(object):

    PROGRAMMER_INIT_PACKET = 1
    PROGRAMMER_STOP_PACKET = 2
    UART_INIT_PACKET = 3
    UART_STOP_PACKET = 4
    RESET_PACKET = 5
    ACK_PACKET = 6
    CLOSE_CONNECTION_PACKET = 7
    NETWORK_CONFIG_PACKET = 8
    SET_OBSERVER_KEY_PACKET = 9
    SET_ENCRYPTION_KEYS_PACKET = 10
    SET_SIGN_KEYS_PACKET = 11
    ENABLE_ENCRYPTION_PACKET = 12
    ENABLE_SIGN_PACKET = 13
    ERROR_PACKET = 14

    LOAD_MCU_INFO_PACKET = 15
    PROGRAM_MEMORY_PACKET = 16
    READ_MEMORY_PACKET = 17
    MEMORY_PACKET = 18
    CMD_PACKET = 19

    UART_CONFIGURATION_PACKET = 20
    UARD_DATA_PACKET = 21


pt = PacketType


class PacketParser(object):

        def __init__(self):
            self.packets_names = dict()
            self.__create_packet_names_dict()
            self.__create_packet_type_byte_mappings()

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

            packet_len = len(data)

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
            t = self._byte_to_type.get(type_byte)

            if t is None:
                raise ex.BrokenPacketError("Unknown packet type")

            return t

        def _get_packet_byte(self, _type):
            b = self._type_to_byte.get(_type)

            if b is None:
                raise ex.BrokenPacketError("Unknown packet type")

            return b

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
            self.packets_names = {
                pt.PROGRAMMER_INIT_PACKET: "ProgrammerInitPacket",
                pt.PROGRAMMER_STOP_PACKET: "ProgrammerStopPacket",
                pt.UART_INIT_PACKET: "UartInitPacket",
                pt.UART_STOP_PACKET: "UartStopPacket",
                pt.RESET_PACKET: "ResetPacket",
                pt.ACK_PACKET: "ACK packet",
                pt.CLOSE_CONNECTION_PACKET: "CloseConnectionPacket",
                pt.NETWORK_CONFIG_PACKET: "NetworkConfigPacket",
                pt.SET_OBSERVER_KEY_PACKET: "SetObserverKeyPacket",
                pt.SET_ENCRYPTION_KEYS_PACKET: "SetEncryptionKeysPacket",
                pt.SET_SIGN_KEYS_PACKET: "SetSignKeysPacket",
                pt.ENABLE_ENCRYPTION_PACKET: "EnableEncryptionPacket",
                pt.ENABLE_SIGN_PACKET: "EnableSignPacket",
                pt.ERROR_PACKET: "Error packet",

                pt.LOAD_MCU_INFO_PACKET: "LoadMcuInfoPacket",
                pt.PROGRAM_MEMORY_PACKET: "ProgramMemoryPacket",
                pt.READ_MEMORY_PACKET: "ReadMemoryPacket",
                pt.MEMORY_PACKET: "MemoryPacket",
                pt.CMD_PACKET: "CMD Packet",

                pt.UART_CONFIGURATION_PACKET: "UartConfigurationPacket",
                pt.UARD_DATA_PACKET: "UartDataPacket"
            }

        def __create_packet_type_byte_mappings(self):
            self._type_to_byte = {
                pt.PROGRAMMER_INIT_PACKET: pl.PL_PROGRAMMER_INIT,
                pt.PROGRAMMER_STOP_PACKET: pl.PL_PROGRAMMER_STOP,
                pt.UART_INIT_PACKET: pl.PL_UART_INIT,
                pt.UART_STOP_PACKET: pl.PL_UART_STOP,
                pt.RESET_PACKET: pl.PL_RESET,
                pt.ACK_PACKET: pl.PL_ACK,
                pt.CLOSE_CONNECTION_PACKET: pl.PL_CLOSE_CONNECTION,
                pt.NETWORK_CONFIG_PACKET: pl.PL_NETWORK_CONFIG,
                pt.SET_OBSERVER_KEY_PACKET: pl.PL_SET_OBSERVER_KEY,
                pt.SET_ENCRYPTION_KEYS_PACKET: pl.PL_SET_ENCRYPTION_KEYS,
                pt.SET_SIGN_KEYS_PACKET: pl.PL_SET_SIGN_KEYS,
                pt.ENABLE_ENCRYPTION_PACKET: pl.PL_ENABLE_ENCRYPTION,
                pt.ENABLE_SIGN_PACKET: pl.PL_ENABLE_SIGN,
                pt.ERROR_PACKET: pl.PL_ERROR,

                pt.LOAD_MCU_INFO_PACKET: pl.PL_LOAD_MCU_INFO,
                pt.PROGRAM_MEMORY_PACKET: pl.PL_PROGRAM_MEMORY,
                pt.READ_MEMORY_PACKET: pl.PL_READ_MEMORY,
                pt.MEMORY_PACKET: pl.PL_MEMORY,
                pt.CMD_PACKET: pl.PL_CMD,

                pt.UART_CONFIGURATION_PACKET: pl.PL_UART_CONFIGURATION,
                pt.UARD_DATA_PACKET: pl.PL_UART_DATA
            }

            self._byte_to_type = dict([v, k] for v, k in
                                      self._type_to_byte.iteritems())
