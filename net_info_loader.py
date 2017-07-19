import serial as ps
import argparse
from time import sleep


phy_modes = {'b': 0, 'g': 1, 'n': 2}
wifi_modes = {'station': 0, 'ap': 1}
channels = range(14)

START_PACKET_BYTE = 0x1B
STOP_PACKET_BYTE = START_PACKET_BYTE


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog="Network Info Loader")

    parser.add_argument("-p", help="Serial port", default="/dev/ttyUSB0")
    parser.add_argument("-ssid", help="SSID name", default=None)
    parser.add_argument("-pwd", help="Password", default=None)
    parser.add_argument("-phy", help="Physical mode. b, g or n", default='n')

    parser.add_argument("-m", help="Mode. Either station or ap",
                        default="station")

    parser.add_argument("-c", help="Channel. Suitable only for AP mode",
                        default="6")

    args = parser.parse_args()

    port = args.p
    ssid = args.ssid
    pwd = args.pwd
    phy = args.phy
    mode = args.m
    channel = int(args.c)

    if ssid is None:
        print("Specify ssid name. Use -ssid option")
        exit(1)

    if pwd is None:
        print("Specify password. Use -pwd option")
        exit(1)

    if phy not in phy_modes:
        print("Wrong physical mode. Must be b, g or n")
        exit(1)

    if mode not in wifi_modes:
        print("Wrong operation mode. Must be eihter station or ap")
        exit(1)

    if channel not in channels:
        print("Wrong channel. Has to be in range from 0 to 13")
        exit(1)

    if mode == 'ap':
        if len(pwd) < 8:
            print("Password hat to be at least 8 bytes long")
            exit(1)

    ssid_len = len(ssid)
    pwd_len = len(pwd)

    network_data = bytearray()
    network_data.append(wifi_modes[mode])
    network_data.append(phy_modes[phy])
    network_data.append(channel)

    network_data.append(ssid_len)
    network_data.extend(bytearray(ssid, encoding='utf-8'))

    network_data.append(pwd_len)
    network_data.extend(bytearray(pwd, encoding='utf-8'))

    packet = bytearray()
    packet.append(START_PACKET_BYTE)

    # Flags
    packet.append(0x00)

    # Packet type
    packet.append(0x17)

    # Length
    packet.append(0)
    packet.append(len(network_data))

    # Payload
    packet.extend(network_data)

    _s = ''
    for p in packet:
        _s += ("0x%02x " % p)

    print("Total length is: " + str(len(packet)))
    print("SSID length is: " + str(ssid_len))
    print("Password length is: " + str(pwd_len))
    print("Sending:\r\n\t%s" % _s)

    ser = ps.Serial(port, 115200)
    ser.write(packet)

    sleep(2.0)
    if ser.in_waiting > 0:
        ack = bytearray(ser.read(ser.in_waiting))

        for a in ack:
            if a != 0xAA:
                print("Something is wrong with connection!")
                print("Got: ".join('0x%02x ' % x for x in ack))
    else:
        print("Missing ACK")
        exit(1)

    exit(0)
