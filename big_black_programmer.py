import avrdude_input as avd
import errors as err
from interactive import InteractiveMode

from network.observer import observe
from network.network_manager import NetworkManager
from network import network_exceptions as net_ex

from programmers.avr.avr_programmer import AvrProgrammer
from programmers import programmer_exceptions as p_ex
from programmers.avr import avr_exceptions as avr_ex
from network.packet_manager import PacketManager, PacketType

import traceback

from time import time
import sys

ESP_PORT = 1000
ERROR_CODE = err.ERROR_OK


def esp_connect():
    try:
        esp_addr = (observe(port), ESP_PORT)
        return NetworkManager(esp_addr)

    except net_ex.NetworkConnectionError as e:
        sys.stderr.write(str(e)+'\r\n')
        exit(err.NETWORK_ERROR)


if __name__ == "__main__":
    parser = avd.create_parser()
    opts = avd.parse(parser)

    port = opts['port']
    mmcu = opts['part']

    flash_op = opts['flash']
    eeprom_op = opts['eeprom']

    hfuse_op = opts['hfuse']
    lfuse_op = opts['lfuse']
    lock_op = opts['lock']

    erase = opts['erase']
    validate = opts['validate']

    if opts['interactive']:
        itv_mode = InteractiveMode()

    if opts['part'] is None:
        print("Please specify the MCU part with -p option.")
        exit(err.ARGUMENTS_ERROR)

    network_manager = esp_connect()
    packet_manager = PacketManager(network_manager)

    try:
        packet_manager.start()
        print("Connected")

        programmer = AvrProgrammer(mmcu, packet_manager)
        print("Initialize programmer")
        programmer.init_programmer()
        print("Main op")

        if erase or ((flash_op is not None) and (flash_op[0] == 'w')):
            print("Erasing chip")
            programmer.send_chip_erase()

        if flash_op:
            op, flash_fname = flash_op[0], flash_op[1]

            if op == 'w':
                print("Loading firmware")
                time0 = time()
                programmer.burn_file(flash_fname, "flash", None, validate)
                print("Flashing time is " + str(round(time() - time0, 3)))

            else:
                print("Reading firmware")
                time0 = time()
                programmer.read_memory("flash", flash_fname)
                print("Reading tim is " + str(round(time() - time0, 3)))

        if eeprom_op:
            op, eeprom_name = eeprom_op[0], eeprom_op[1]

            if op == 'w':
                print("Burn eeprom")
                time0 = time()
                programmer.burn_file(eeprom_name, 'eeprom', None, validate)
                print("Flashing time is " + str(round(time() - time0, 3)))

            else:
                programmer.read_memory("eeprom", eeprom_name)

        h_fuse = None
        l_fuse = None

        if lfuse_op:
            op, lfuse_val = lfuse_op[0], lfuse_op[1]

            if op == 'w':
                print("Write low fuse 0x%02x" % lfuse_val)
                programmer.write_lfuse(lfuse_val)
                l_fuse = programmer.read_lfuse()

                if lfuse_val != l_fuse:
                    raise p_ex.HardwareError("Wrong low fuse was written: "
                                             "0x%02x != 0x%02x" %
                                             (lfuse_val, l_fuse))
            else:
                l_fuse = programmer.read_lfuse()

        if hfuse_op:
            op, hfuse_val = hfuse_op[0], hfuse_op[1]

            if op == 'w':
                print("Write high fuse 0x%02x" % hfuse_val)
                programmer.write_hfuse(hfuse_val)
                h_fuse = programmer.read_hfuse()

                if hfuse_val != h_fuse:
                    raise p_ex.HardwareError("Wrong high fuse was written. "
                                             "0x%02x != 0x%02x" %
                                             (hfuse_val, h_fuse))
            else:
                h_fuse = programmer.read_hfuse()

        if h_fuse:
            print("High fuse is 0x%02x " % h_fuse)

        if l_fuse:
            print("Low fuse is 0x%02x " % l_fuse)

    except net_ex.NetworkBaseError as e:
        sys.stderr.write(str(e)+'\r\n')
        ERROR_CODE = err.NETWORK_ERROR

    except p_ex.ProgrammerBaseError as e:
        sys.stderr.write(str(e)+'\r\n')
        ERROR_CODE = err.AVR_ERROR

    finally:
        try:
            programmer.stop_programmer()
        finally:
            traceback.print_exc()
            packet_manager.stop()
            exit(ERROR_CODE)
