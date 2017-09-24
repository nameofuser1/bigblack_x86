from .packet_parser import PacketType as pt
from . import programmer_exceptions as ex

from network import protocol as pl

from abc import abstractmethod, ABCMeta
from intelhex import IntelHex


PACKET_WAIT_TIMEOUT = 1.


class HardwareProgrammer(object):
    """
    Wraps either HardwareProgrammer or StmProgrammer
    """
    __metaclass__ = ABCMeta

    MEMORY_EEPROM_BYTE = 0x01
    MEMORY_FLASH_BYTE = 0x00


    def __init__(self, packet_manager):
        print("Saving packet manager")
        self.packet_manager = packet_manager

    @abstractmethod
    def _write_file_to_eeprom(self, eeprom_file, start_address, validate):
        pass

    @abstractmethod
    def _write_file_to_flash(self, flash_file, start_address, validate):
        pass

    @abstractmethod
    def _read_flash_memory(self):
        pass

    @abstractmethod
    def _read_eeprom_memory(self):
        pass

    def burn_file(self, fname, memory, start_address=None, validate=False):
        extention = fname.split('.')[-1]
        intel_hex = IntelHex()

        if extention == 'hex':
            intel_hex.fromfile(fname, format='hex')
        elif extention == 'bin':
            intel_hex.fromfile(fname, format='bin')
        else:
            raise ValueError("Wrong file extention: " + extention)

        if memory == 'flash':
            self._write_file_to_flash(intel_hex, start_address, validate)
        elif memory == 'eeprom':
            self._write_file_to_eeprom(intel_hex, start_address, validate)
        else:
            raise ValueError("Wrong memory specified: " + memory)

    def read_memory(self, memory_t, fname=None):
        if memory_t == 'flash':
            memory = self._read_flash_memory()
        elif memory_t == 'eeprom':
            memory = self._read_eeprom_memory()

        if fname is not None:
            self._save_memory(fname, memory, memory_t)

        return memory

    def send(self, raw_data, packet_type):
        self.packet_manager.send_raw(raw_data, packet_type)

    def read_packet(self, timeout=PACKET_WAIT_TIMEOUT):
        return self.packet_manager.read_packet(timeout=timeout)

    def send_recv(self, raw_data, packet_type,
                  timeout=PACKET_WAIT_TIMEOUT):
        self.send(raw_data, packet_type)
        return self.read_packet(timeout=timeout)

    # ######################################
    # Sends command which is byte array
    # ######################################
    def send_command(self, command,
                     timeout=PACKET_WAIT_TIMEOUT,
                     wait_answer=True):

        self.send(command, pt.CMD_PACKET)

        if wait_answer:
            return self.read_packet(timeout=timeout)

    # ####################################
    # Creates command packet
    # from 4 bytes
    # ####################################
    def create_command(self, b1, b2, b3, b4):
        cmd = [b1, b2, b3, b4]
        return bytearray(cmd)

    def _send_flash_prog_mem_packet(self, raw_data, addr):
        self.__send_prog_mem_packet(raw_data, addr, self.MEMORY_FLASH_BYTE)

    def _send_eeprom_prog_mem_packet(self, raw_data, addr):
        self.__send_prog_mem_packet(raw_data, addr, self.MEMORY_EEPROM_BYTE)

    def __send_prog_mem_packet(self, raw_data, address, memory_type_byte):
        """
        Creates program memory packet from given data

        raw_data            --- bytes to be written into memory
        address             --- address where to start writing at
        memory_type_byte    --- either MEMORY_EEPROM_BYTE or MEMORY_FLASH_BYTE

        returns None
        """
        # 4 bytes for address and 1 byte for memory type
        header_size = 5

        raw_packet = bytearray(len(raw_data) + header_size)
        raw_packet[0:4] = self.int_to_bytes(address)
        raw_packet[4] = memory_type_byte
        raw_packet[5:] = raw_data[:]

        ack = self.send_recv(raw_packet, pt.PROG_MEM_PACKET)
        self._check_packet(ack, pt.ACK_PACKET)

    def _read_flash_memory_chunk(self, address, bytes_to_read):
        return self._read_memory_chunk(address, bytes_to_read,
                                       HardwareProgrammer.MEMORY_FLASH_BYTE)

    def _read_eeprom_memory_chunk(self, address, bytes_to_read):
        return self._read_memory_chunk(address, bytes_to_read,
                                       HardwareProgrammer.MEMORY_EEPROM_BYTE)

    def _read_memory_chunk(self, address, bytes_to_read, memory_type):
        # 1 byte for memory type
        # 4 bytes for start address
        # 4 bytes for number of bytes to read
        packet_size = 9
        read_data = bytearray(packet_size)

        read_data[0] = memory_type
        read_data[1:5] = self.int_to_bytes(address)[0:4]
        read_data[5:9] = self.int_to_bytes(bytes_to_read)[0:4]

        memory_packet = self.send_recv(read_data, pt.READ_MEM_PACKET,
                                       timeout=20)
        self._check_packet(memory_packet, pt.MEMORY_PACKET)

        return bytearray(memory_packet['data'])

    def _read_memory(self, memory_type_byte):
        packet_header_size = 3
        max_bytes_to_read = pl.MAX_PACKET_LENGTH - packet_header_size

        if max_bytes_to_read % 2 != 0:
            max_bytes_to_read -= 1

        if memory_type_byte == HardwareProgrammer.MEMORY_FLASH_BYTE:
            read_chunk = self._read_flash_memory_chunk
            memory_size = self.flash_size

        elif memory_type_byte == HardwareProgrammer.MEMORY_EEPROM_BYTE:
            read_chunk = self._read_eeprom_memory_chunk
            memory_size = self.eeprom_size

        memory = bytearray()

        data_cnt = 0
        address = 0

        while data_cnt < memory_size:
            bytes_to_read = min(max_bytes_to_read, memory_size - data_cnt)
            chunk = read_chunk(address, bytes_to_read)
            memory.extend(chunk)

            data_cnt += bytes_to_read

            if memory_type_byte == HardwareProgrammer.MEMORY_FLASH_BYTE:
                address = data_cnt // 2
            else:
                address = data_cnt

        return memory

    def _save_memory(self, fname, memory, memory_type):
        """
        Saves memory either into binary file or into hex using
            IntelHex library

        fname               --- filename to save into.
                                Must have extension .bin or .hex

        memory              --- bytearray which contains memory

        memory_type_byte    --- specifies memory type: flash or eeprom.
                                    If memory is flash and file is hex then
                                    memory will be cleared from 0xFF 0xFF
                                    before saving.

        Returns None
        """
        extension = fname.split('.')[-1]

        if extension == 'bin':
            bin_mem = self._make_bin_map(memory, memory_type)
            f = open(fname, 'wb')
            self._save_bin(f, bin_mem)

        elif extension == 'hex':
            memory_map = self._make_hex_map(memory, memory_type)
            f = open(fname, 'w')
            self._save_hex(f, memory_map)

        else:
            raise ValueError("Wrong file extention: " + extension)

        f.close()

    def _save_bin(self, fobj, memory):
        intel_hex = IntelHex()
        intel_hex.frombytes(memory)
        intel_hex.tofile(fobj, 'bin')

    def _save_hex(self, fobj, memory):
        intel_hex = IntelHex()
        intel_hex.fromdict(memory)
        intel_hex.tofile(fobj, 'hex')

    def _make_hex_map(self, memory, memory_type):
        """
        If EEPROM memory is given, converts array to dictionary.
        For FLASH memory it clears it from 0xFF 0xFF and converts data into
            dictionary with address as key and value as address byte value

        memory              --- bytearray which contains memory
        memory_type_byte    --- specifies memory. Either flash or eeprom

        returns dict[address] = byte
        """

        if memory_type == 'eeprom':
            return self._list2dict(memory)

        mem_map = {}

        for addr in range(0, len(memory), 2):
            low_byte = memory[addr]
            high_byte = memory[addr+1]

            if (low_byte != 0xFF) and (high_byte != 0xFF):
                mem_map[addr] = low_byte
                mem_map[addr+1] = high_byte

        return mem_map

    def _list2dict(self, l):
        d = {}
        for i in range(len(l)):
            d[i] = l[i]

        return d

    def _make_bin_map(self, memory, memory_type):
        """
        Does nothing for EEPROM memory and deletes unprogrammed memory from the
            end of FLASH memory

        memory              --- bytearray which contains memory
        memory_type_byte    --- specifies memory type. Either flash or eeprom

        return bytearray with deleted 0xFF 0xFF from the end if memory is FLASH
            and return copy of data if memory is EEPROM
        """
        cleared_memory = bytearray(memory)

        if memory_type == 'eeprom':
            return cleared_memory

        # Flash memory
        free_mem = None

        for i in range(0, len(memory), 2):
            low_b = memory[i]
            high_b = memory[i+1]

            if (low_b == high_b == 0xFF) and (free_mem is None):
                free_mem = i

            elif (low_b != 0xFF) or (high_b != 0xFF) and (free_mem is not None):
                free_mem = None

        if free_mem is not None:
            del cleared_memory[free_mem:]

        return cleared_memory

    def _check_packet(self, packet, exp_type):
        if packet['type'] != exp_type:
            packet_name = self.packet_manager.get_packet_name(packet)
            exp_name = self.packet_manager.get_packet_name_by_type(exp_type)

            raise ex.WrongPacketError("Expected packet %s. Got %s packet" %
                                      (exp_name, packet_name))

    # #############################
    #   Converts 4-bytes integer
    #   to bytes list
    # #############################
    def int_to_bytes(self, i):
        return [((i >> 24) & 0xFF), ((i >> 16) & 0xFF),
                ((i >> 8) & 0xFF), (i & 0xFF)]
