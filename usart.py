from observer import observe, DEFAULT_PORT
from packet_manager import PacketManager
from packet_parser import PacketType
from utils.Exceptions import WrongPacketException, DeviceError
from protocol import *
from errors import *
import sys
import signal
import argparse


BAUDRATE_9600   = 9600
BAUDRATE_19200  = 19200
BAUDRATE_38400  = 38400
BAUDRATE_57600  = 57600
BAUDRATE_74880  = 74880
BAUDRATE_115200 = 115200

PARITY_NONE = 'n'
PARITY_EVEN = 'e'
PARITY_ODD = 'o'

DATA_BITS_8 = 8
DATA_BITS_9 = 9

STOP_BITS_1 = 1
STOP_BITS_2 = 2


bd_dict = {BAUDRATE_9600: USART_BAUDRATE_9600, BAUDRATE_19200: USART_BAUDRATE_19200,
           BAUDRATE_38400: USART_BAUDRATE_38400, BAUDRATE_57600: USART_BAUDRATE_57600,
           BAUDRATE_74880: USART_BAUDRATE_74880, BAUDRATE_115200: USART_BAUDRATE_115200}

pt_dict = {PARITY_NONE: USART_PARITY_NONE,
           PARITY_EVEN: USART_PARITY_EVEN,
           PARITY_ODD: USART_PARITY_ODD}

db_dict = {DATA_BITS_8: USART_DATA_BITS_8,
           DATA_BITS_9: USART_DATA_BITS_9}

sb_dict = {STOP_BITS_1: USART_STOP_BITS_1,
           STOP_BITS_2: USART_STOP_BITS_2}


running = False


def signal_handler(sig, frame):
    if sig == signal.SIGQUIT:
        global running
        running = False


def get_raw_usart_config(bd, pt, db, sb):
    config = bytearray(USART_PACKET_DATA_SIZE)

    config[USART_BAUDRATE_BYTE_OFFSET] = bd_dict[bd]
    config[USART_PARITY_BYTE_OFFSET] = pt_dict[pt]
    config[USART_DATA_BITS_BYTE_OFFSET] = db_dict[db]
    config[USART_STOP_BITS_BYTE_OFFSET] = sb_dict[sb]

    return config


if __name__ == "__main__":

    parser = argparse.ArgumentParser(prog="flasher")
    parser.add_argument("-bd", help="Baudrate", default=BAUDRATE_9600)
    parser.add_argument('-pt', help='Parity', default=PARITY_NONE)
    parser.add_argument('-db', help='Data bits', default=DATA_BITS_8)
    parser.add_argument('-sb', help='Stop bits', default=STOP_BITS_1)
    parser.add_argument("-p", help="Set local port", type=int, default=DEFAULT_PORT)
    args = parser.parse_args()

    bd = parser.bd
    pt = parser.pt
    db = parser.db
    sb = parser.sb
    port = args.p

    if bd not in bd_dict:
        sys.stderr.write("Wrong baudrate")
        exit(USART_ERROR)

    if pt not in pt_dict:
        sys.stderr.write("Wrong parity")
        exit(USART_ERROR)

    if db not in db_dict:
        sys.stderr.write("Wrong data bits")
        exit(USART_ERROR)

    if sb not in sb_dict:
        sys.stderr.write("Wrong stop bits")
        exit(USART_ERROR)

    signal.signal(signal.SIGQUIT, signal_handler)
    usart_raw_config = get_raw_usart_config(bd, pt, db, sb)

    packet_manager = None

    try:
        esp_addr = observe(port)

        packet_manager = PacketManager(esp_addr)
        packet_manager.start()

        conf_packet = packet_manager.create_packet(usart_raw_config, PacketType.USART_CONF_PACKET)
        packet_manager.send(conf_packet)

        packet = packet_manager.wait_for_packet(ACK_WAIT_TIMEOUT)

        running = True
        while running:
            try:
                packet = packet_manager.wait_for_packet(PACKET_WAIT_TIMEOUT)

                if packet["type"] == PacketType.ERROR_PACKET:
                    raise DeviceError(packet["data"])

                if packet["type"] != PacketType.USART_PACKET:
                    raise WrongPacketException("Got %s packet instead of usart one" %
                                               packet_manager.get_packet_name(packet))

                sys.stdout.write(packet)
            except TimeoutError:
                pass

    except TimeoutError as e:
        sys.stderr.write(str(e))
        exit(CONNECTION_ERROR)

    except DeviceError as e:
        sys.stderr.write(str(e))
        exit(DEVICE_ERROR)

    except KeyboardInterrupt:
        packet_manager.stop()