from . import avr_exceptions as ex
from .config_parser import ConfParser
from .avr_defs import Avr

from programmers.hardware_programmer import HardwareProgrammer
from programmers.packet_parser import PacketType as pt
from programmers import programmer_exceptions as p_ex

from network import protocol as pl

import math
from time import sleep

import os
dir_path = os.path.dirname(os.path.realpath(__file__))


class AvrProgrammer(HardwareProgrammer):

    ADDRESS_SIZE = 4
    TYPE_SIZE = 1

    def __init__(self, part_name, network_manager):
        super(AvrProgrammer, self).__init__(network_manager)

        conf_parser = ConfParser()
        conf_parser.parse(dir_path + "/parts.conf")
        mcu_info = conf_parser.get_parts()[part_name]

        self.max_pgm_memory_data_len = pl.PL_MAX_DATA_LENGTH

        print("AvrProgrammer max_pgm_memory len: " +
              str(self.max_pgm_memory_data_len))

        signature_codes = mcu_info["signature"].split(' ')
        self.vendor_code = int(signature_codes[0], 16)
        self.part_family = int(signature_codes[1], 16)
        self.part_number = int(signature_codes[2], 16)

        pgm_enable_pattern = mcu_info["pgm_enable"].replace(" ", "")
        self.pgm_enable = self.create_cmd_from_pattern(pgm_enable_pattern)

        self.eeprom_write = mcu_info["memory_eeprom"]["write"].replace(" ", "")
        self.eeprom_read = mcu_info["memory_eeprom"]["read"].replace(" ", "")
        self.eeprom_size = int(mcu_info["memory_eeprom"]["size"])

        self.eeprom_wait = int(mcu_info["memory_eeprom"]["min_write_delay"])
        # round to ms
        self.eeprom_wait = int(math.floor(self.eeprom_wait // 1000) + 1)

        self.flash_size = int(mcu_info["memory_flash"]["size"])
        self.flash_read_lo = mcu_info["memory_flash"]["read_lo"].\
            replace(" ", "")
        self.flash_read_hi = mcu_info["memory_flash"]["read_hi"].\
            replace(" ", "")

        flash_paged = mcu_info["memory_flash"].get("paged")

        if flash_paged is None or flash_paged == "no":
            self.flash_paged = False
            self.flash_page_num = 0
            self.flash_page_size = 0
            self.flash_write_lo = mcu_info["memory_flash"]["write_lo"].\
                replace(" ", "")
            self.flash_write_hi = mcu_info["memory_flash"]["write_hi"].\
                replace(" ", "")
            self.write_page_pattern = None

            # ###################################
            #   Timer on stm is with 1 ms period
            #   So we round us to ms
            # ###################################
            self.flash_wait = int(mcu_info["memory_flash"]["min_write_delay"])
            self.flash_wait = math.floor(self.flash_wait//1000) + 1

        else:
            self.flash_paged = True
            self.flash_page_num = int(mcu_info["memory_flash"]["num_pages"])
            self.flash_page_size = int(mcu_info["memory_flash"]["page_size"])
            self.flash_write_lo = mcu_info["memory_flash"]["loadpage_lo"].\
                replace(" ", "")
            self.flash_write_hi = mcu_info["memory_flash"]["loadpage_hi"].\
                replace(" ", "")
            self.flash_wait = 0
            self.write_page_pattern = mcu_info["memory_flash"]["writepage"].\
                replace(" ", "")

    # #######################################
    # Initialize programmer (usart possible)
    # #######################################
    def init_programmer(self):
        ack = self.send_recv([pl.PL_AVR_PROGRAMMER_BYTE], pt.PROG_INIT_PACKET)
        self._check_packet(ack, pt.ACK_PACKET)

        self.send_mcu_init()
        self.validate_signature()

    def validate_signature(self):
        """
        Reads signature and compares it with that which is in
            parts configuration
        """
        print("Validating signature")
        signature = self.read_signature()

        if (int(signature[0]) != self.vendor_code) or\
                (int(signature[1]) != self.part_family)\
                or (int(signature[2]) != self.part_number):

            raise ex.DeviceError("Wrong device signature")

        print("Device signature is: 0x%02x 0x%02x 0x%02x" %
              (signature[0], signature[1], signature[2]))

        return True

    # ######################################
    # Send needed mcu info
    # Should get acknowledge packet
    # ######################################
    def send_mcu_init(self):
        print("AvrProgrammer send init")
        init_data = bytearray()

        init_data.append(len(self.flash_write_lo))
        init_data.extend([ord(c) for c in self.flash_write_lo])

        init_data.append(len(self.flash_write_hi))
        init_data.extend([ord(c) for c in self.flash_write_hi])

        init_data.append(len(self.flash_read_lo))
        init_data.extend([ord(c) for c in self.flash_read_lo])

        init_data.append(len(self.flash_read_hi))
        init_data.extend([ord(c) for c in self.flash_read_hi])

        init_data.append(self.flash_wait)

        init_data.append(len(self.eeprom_write))
        init_data.extend([ord(c) for c in self.eeprom_write])

        init_data.append(len(self.eeprom_read))
        init_data.extend([ord(c) for c in self.eeprom_read])

        init_data.append(self.eeprom_wait)
        init_data.extend(self.pgm_enable)

        packet = self.send_recv(init_data, pt.AVR_PROG_INIT_PACKET)
        self._check_packet(packet, pt.CMD_PACKET)

        if int(packet["data"][0]) == 0:
            raise ex.DeviceError("Can't enter pgm mode")

        print("Successfully initialized")
        return True

    # #########################################
    # Send stop packet
    # Must get acknowledge packet
    # #########################################
    def send_stop(self):
        packet = self.send_recv([], pt.STOP_PACKET)
        self._check_packet(packet, pt.ACK_PACKET)

    # ########################################
    #   Performs chip erase
    # ########################################
    def send_chip_erase(self):
        cmd = self.create_command(Avr.AVR_CHP_ERS_B1,
                                  Avr.AVR_CHP_ERS_B2,
                                  Avr.AVR_CHP_ERS_B3,
                                  Avr.AVR_CHP_ERS_B4)
        packet = self.send_command(cmd)
        sleep(0.050)

        packet = self._check_packet(packet, pt.CMD_PACKET)

    # #####################################
    #   Check for busy by polling command
    #   !!!Works not everywhere!!!
    # #####################################
    def check_for_busy(self):
        cmd = self.create_command(Avr.AVR_POLL_B1,
                                  Avr.AVR_POLL_B2,
                                  Avr.AVR_POLL_B3,
                                  Avr.AVR_POLL_B4)
        packet = self.send_command(cmd)

        self._check_packet(packet, pt.CMD_PACKET)
        return int(packet["data"][3]) & 0x01

    def load_eeprom_page(self, addr_lsb, byte):
        cmd = self.create_command(Avr.AVR_LD_EMEM_B1,
                                  Avr.AVR_LD_EMEM_B2,
                                  addr_lsb,
                                  byte)
        self.send_command(cmd)

    def load_extended_addr(self, ext_addr):
        cmd = self.create_command(Avr.AVR_LD_EXT_ADDR_B1,
                                  Avr.AVR_LD_EXT_ADDR_B2,
                                  ext_addr,
                                  Avr.AVR_LD_EXT_ADDR_B4)
        self.send_command(cmd)

    # ######################################
    # Read signature codes
    # ######################################
    def read_signature(self):
        sign = list()
        sign.append(self.read_vendor_code())
        sign.append(self.read_part_family())
        sign.append(self.read_part_number())

        return sign

    def read_vendor_code(self):
        cmd = self.create_command(Avr.AVR_RD_SIG_B1,
                                  Avr.AVR_RD_SIG_B2,
                                  Avr.AVR_RD_VENDOR_CODE,
                                  Avr.AVR_RD_SIG_B4)
        packet = self.send_command(cmd)

        return int(packet["data"][3])

    def read_part_family(self):
        cmd = self.create_command(Avr.AVR_RD_SIG_B1,
                                  Avr.AVR_RD_SIG_B2,
                                  Avr.AVR_RD_PART_FAMILY,
                                  Avr.AVR_RD_SIG_B4)
        packet = self.send_command(cmd)

        return int(packet["data"][3])

    def read_part_number(self):
        cmd = self.create_command(Avr.AVR_RD_SIG_B1,
                                  Avr.AVR_RD_SIG_B2,
                                  Avr.AVR_RD_PART_NUMBER,
                                  Avr.AVR_RD_SIG_B4)
        packet = self.send_command(cmd)

        return int(packet["data"][3])

    def read_hfuse(self):
        cmd = self.create_command(Avr.AVR_RD_HFUSE_B1,
                                  Avr.AVR_RD_HFUSE_B2,
                                  Avr.AVR_RD_HFUSE_B4,
                                  Avr.AVR_RD_HFUSE_B4)
        packet = self.send_command(cmd)

        return int(packet["data"][3])

    def read_lfuse(self):
        cmd = self.create_command(Avr.AVR_RD_LFUSE_B1,
                                  Avr.AVR_RD_LFUSE_B2,
                                  Avr.AVR_RD_LFUSE_B3,
                                  Avr.AVR_RD_LFUSE_B4)
        packet = self.send_command(cmd)

        return int(packet["data"][3])

    def read_lock_bits(self):
        cmd = self.create_command(Avr.AVR_RD_LCK_B1,
                                  Avr.AVR_RD_LCK_B2,
                                  Avr.AVR_RD_LCK_B3,
                                  Avr.AVR_RD_LCK_B4)
        packet = self.send_command(cmd)

        return int(packet["data"][3])

    def read_extended_fuse(self):
        cmd = self.create_command(Avr.AVR_RD_EXFUSE_B1,
                                  Avr.AVR_RD_EXFUSE_B2,
                                  Avr.AVR_RD_EXFUSE_B3,
                                  Avr.AVR_RD_EXFUSE_B5)
        packet = self.send_command(cmd)

        return int(packet["data"][3])

    def write_hfuse(self, byte):
        cmd = self.create_command(Avr.AVR_WRT_HFUSE_B1,
                                  Avr.AVR_WRT_HFUSE_B2,
                                  Avr.AVR_WRT_HFUSE_B3, byte)

        packet = self.send_command(cmd)
        self._check_packet(packet, pt.CMD_PACKET)

    def write_lfuse(self, byte):
        cmd = self.create_command(Avr.AVR_WRT_LFUSE_B1,
                                  Avr.AVR_WRT_LFUSE_B2,
                                  Avr.AVR_WRT_LFUSE_B3, byte)

        packet = self.send_command(cmd)
        self._check_packet(packet, pt.CMD_PACKET)

    def write_lock_bits(self, byte):
        cmd = self.create_command(Avr.AVR_WRT_LCK_B1,
                                  Avr.AVR_WRT_LCK_B2,
                                  Avr.AVR_WRT_LCK_B3, byte)

        packet = self.send_command(cmd)
        self._check_packet(packet, pt.CMD_PACKET)

    def write_extended_fuse(self, byte):
        cmd = self.create_command(Avr.AVR_WRT_EXTFUSE_B1,
                                  Avr.AVR_WRT_EXTFUSE_B2,
                                  Avr.AVR_WRT_EXTFUSE_B3, byte)

        packet = self.send_command(cmd)
        self._check_packet(packet, pt.CMD_PACKET)

    def _read_eeprom_memory(self):
        """
        Reads the full contents of EEPROM MEMORY
        """
        return self._read_memory(HardwareProgrammer.MEMORY_EEPROM_BYTE)

    def _read_flash_memory(self):
        """
        Reads only programmed part of FLASH MEMORY
        """
        return self._read_memory(HardwareProgrammer.MEMORY_FLASH_BYTE)

    # ##################################################
    # Writes file to EEPROM
    # ##################################################
    def _write_file_to_eeprom(self, eeprom_mem, start_address,
                              validate):
        """
        Writes hex file into eeprom at specified address
        """
        # 4 bytes for address and 1 byte for memory type
        header_size = 5
        max_chunk_size = pl.MAX_PACKET_LENGTH - header_size

        addresses = eeprom_mem.addresses()

        data = bytearray(max_chunk_size)
        data_cnt = 0

        current_addr = 0
        prev_addr = 0

        for addr in addresses:
            addr_diff = addr - prev_addr

            if (data_cnt == max_chunk_size) or (addr_diff > 1):
                if data_cnt != 0:
                    self._send_eeprom_prog_mem_packet(data[0:data_cnt],
                                                      current_addr)
                    data_cnt = 0

            if data_cnt == 0:
                current_addr = addr

            data[data_cnt] = eeprom_mem[addr]
            data_cnt += 1

            prev_addr = addr

        if data_cnt > 0:
            self._send_eeprom_prog_mem_packet(data[0:data_cnt],
                                              current_addr)

    # ####################################
    # Writes given file to flash
    # Raises IOError exception
    # ####################################
    def _write_file_to_flash(self, flash_mem, start_address, validate):
        if self.flash_paged:
            """
            First we read file into dictionary which contains pairs
                [address] = value
            """
            print("Writing flash!")
            memory_map = flash_mem.todict()

            mapped_memory = {}
            used_pages = {}
            for address in memory_map:
                # because AVR has 16 bit words per addr
                mapped_addr = address // 2
                page = self._get_flash_page(mapped_addr)

                # fill in the whole page
                if page not in used_pages:
                    memory_page = self._process_page(memory_map, page)
                    mapped_memory[page] = memory_page
                    used_pages[page] = True

            # 4 bytes for address and 1 byte for memory type
            packet_header_size = 5
            bytes_for_data = pl.MAX_PACKET_LENGTH - 5

            # we need to send even number of bytes
            if bytes_for_data % 2 != 0:
                bytes_for_data -= 1

            for memory_page_id in mapped_memory:
                memory_page = mapped_memory[memory_page_id]
                tupled_data = memory_page['data']
                data = bytearray(len(tupled_data*2))

                for i in range(len(tupled_data)):
                    data[i*2] = tupled_data[i][0]
                    data[i*2 + 1] = tupled_data[i][1]

                data_len = len(data)

                raw_data_packets = (data_len // pl.MAX_PACKET_LENGTH) + 1
                len_with_headers = data_len +\
                    packet_header_size * raw_data_packets

                packets_to_send = int(len_with_headers //
                                      pl.MAX_PACKET_LENGTH) + 1

                write_address = memory_page['data_start_addr']
                offset = 0
                for i in range(packets_to_send):
                    bytes_to_send = min(data_len - offset, bytes_for_data)
                    packet_data = data[offset:offset + bytes_to_send]

                    self._send_flash_prog_mem_packet(packet_data, write_address)

                    offset += bytes_to_send
                    write_address += bytes_to_send // 2

                start_addr = self._get_flash_page_addresses(memory_page_id)[0]
                self.flash_write_mem_page(start_addr)

    def _process_page(self, memory_map, page):
        """
        """
        start_addr, last_addr = self._get_flash_page_addresses(page)

        not_mapped_addr = start_addr*2
        max_not_mapped_addr = last_addr*2

        memory_page = {'data': [], 'data_start_addr': None}

        while not_mapped_addr <= max_not_mapped_addr:
            high_byte = memory_map.get(not_mapped_addr)
            low_byte = memory_map.get(not_mapped_addr+1)

            # Set the start address of data in page
            # in order to avoid filling gaps between the first
            # page address and adress where data starts
            if memory_page['data_start_addr'] is None:
                if (low_byte is not None) or (high_byte is not None):
                    mapped_addr = not_mapped_addr // 2
                    memory_page['data_start_addr'] = mapped_addr

            not_mapped_addr += 2

            # Both bytes exists then just add them to result
            if (low_byte is not None) and (high_byte is not None):
                memory_page['data'].append((high_byte, low_byte))

            # If we find a gap in page then fill it in with 0xFF
            # Otherwise if it is the end of data in page just do
            # nothing
            elif (low_byte is None) and (high_byte is None) and \
                    (memory_page['data_start_addr'] is not None):
                empty_counter = 0

                while (memory_map.get(not_mapped_addr) is None) and\
                        (not_mapped_addr <= max_not_mapped_addr):

                    empty_counter += 1
                    not_mapped_addr += 1

                if not_mapped_addr > max_not_mapped_addr:
                    # END OF DATA IN PAGE
                    break
                else:
                    # FOUND A GAP
                    # If empty counter is odd than it will leave
                    # last low byte unfilled and on the next
                    # iteration we will fill it in the condition
                    # below
                    for i in xrange(empty_counter, 2):
                        memory_page['data'].append((0xFF, 0xFF))

            elif high_byte is None:
                # Gap of one byte size
                high_byte = 0xFF
                memory_page['data'].append(high_byte, low_byte)

            elif low_byte is None:
                # Last byte is missing
                # Next iteration will find out if it is a gap or
                # the end of data in a page
                low_byte = 0xFF
                memory_page['data'].append(high_byte, low_byte)

        return memory_page

    def _get_flash_page(self, addr):
        """
        Computes page number which contains given address
        """
        self.__check_for_paged_flash()
        self.__check_addr_validity(addr, memory='flash')

        for page in range(self.flash_page_num):
            start_addr, last_addr = self._get_flash_page_addresses(page)

            if addr < last_addr:
                return int(page)

    def _get_flash_page_addresses(self, page):
        self.__check_for_paged_flash()
        self.__check_flash_page_validity(page)

        start_addr = self.__get_flash_page_start_addr(page)
        last_addr = self.__get_flash_page_last_addr(page)

        return start_addr, last_addr

    def __get_flash_page_start_addr(self, page):
        return int(page * self.flash_page_size // 2)

    def __get_flash_page_last_addr(self, page):
        return int((page + 1) * self.flash_page_size // 2) - 1

    def __get_max_addr(self, memory='flash'):
        if memory == 'flash':
            max_addr = (self.flash_size // 2) - 1
        elif memory == 'eeprom':
            max_addr = self.eeprom_size - 1
        else:
            raise ex.InternalError("Wrong memory specified %s" % memory)

        return int(max_addr)

    def __check_addr_validity(self, addr, memory='flash'):
        max_addr = self.__get_max_addr(memory)

        if (addr > max_addr) or (addr < 0):
            raise ex.InternalError("Given address is not valid. %d" % addr)

    def __check_flash_page_validity(self, page):
        if (page > self.flash_page_num) or (page < 0):
            raise ex.InternalError("Given page is not valid. %d", page)

    def __check_for_paged_flash(self):
        if not self.flash_paged:
            raise ex.InternalError("Flash memory is not paged")

    # ########################################
    #   Writes page with pre-filled buffer
    # ########################################
    def flash_write_mem_page(self, addr):
        """
        Call it to write buffered page.

        addr    --- first address of the page
        """
        cmd = self.create_cmd_from_pattern(self.write_page_pattern, addr)
        res_packet = self.send_recv(cmd, pt.CMD_PACKET)

        self._check_packet(res_packet, pt.CMD_PACKET)
        return True

    # ################################################
    #  Creates command without input
    #  by pattern from parts.conf
    # ################################################
    def create_cmd_from_pattern(self, pattern, addr=0):
        print("Addr in create cmd from pattern: " + str(addr))

        cmd = [0]*4
        cmd_byte_offset = 0
        cmd_current_bit = 7

        if pattern is not None:
            i = 0
            while i < len(pattern):

                if pattern[i] == '1':
                    cmd[cmd_byte_offset] |= (1 << cmd_current_bit)

                elif pattern[i] == '0':
                    cmd[cmd_byte_offset] &= ~(1 << cmd_current_bit)

                elif pattern[i] == 'x':
                    pass

                elif pattern[i] == 'a':
                    i += 1
                    address_shift = ""

                    while (pattern[i] >= '0') and (pattern[i] <= '9'):
                        address_shift += pattern[i]
                        i += 1

                    i -= 1  # last i += 1 + cycle i+1 causes missing next char

                    address_shift = int(address_shift)
                    cmd[cmd_byte_offset] |= (
                        ((addr >> address_shift) & 0x01) << cmd_current_bit)

                cmd_current_bit -= 1
                if cmd_current_bit < 0:
                    # i.e. = 7. Because = 7 sends error about unused local var
                    cmd_current_bit += 8
                    cmd_byte_offset += 1

                i += 1

            return cmd

        return None
