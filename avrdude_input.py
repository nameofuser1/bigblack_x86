import argparse


__memories = ['flash', 'eeprom', 'hfuse', 'lfuse', 'lock']
__operations = ['w', 'r']
__files_types = ['hex', 'bin']
__fuses = range(256)


def __parse_memory_op(op_str):
    splitted = op_str.split(':')

    if len(splitted) != 3:
        raise ValueError()

    memory = splitted[0]
    op = splitted[1]
    file_or_fuse = splitted[2]

    if memory not in __memories:
        raise ValueError("Wrong memory type. Could be flash, eeprom, "
                         "hfuse, lfuse")

    if op not in splitted:
        raise ValueError("Wrong memory operation. Could be either w or r")

    if memory in __memories[2:]:
        if op == 'w':
            file_or_fuse = int(file_or_fuse, 16)

            if file_or_fuse not in __fuses:
                raise ValueError("Wrong " + memory + " value %s. Must be in "
                                 "range 0:0xFF" % hex(file_or_fuse))

    elif (memory in __memories[0:2]) or (op == 'r'):
        _ftype = file_or_fuse.split('.')[-1]

        if _ftype not in __files_types:
            raise ValueError("Wrong file. Could be either hex or binary")

    return memory, op, file_or_fuse


def create_parser():
    parser = argparse.ArgumentParser(prog="avr flasher")

    parser.add_argument("-p", help="Part number")
    parser.add_argument("-U", action='append', help="Memory operation")
    parser.add_argument("-P", help="Port name")
    parser.add_argument("-e", action="store_true", help="Chip erase")
    parser.add_argument("-v", action="store_true", help="Enable verification")
    parser.add_argument("-t", action="store_true", help="Interactive mode")

    return parser


def parse(parser, args_list=None):
    args = parser.parse_args(args_list)

    parsed = {}
    parsed['interactive'] = args.t
    parsed['erase'] = args.e
    parsed['validate'] = args.v
    parsed['port'] = args.P
    parsed['part'] = args.p

    if args.U is not None:
        for memory_op in args.U:
            memory, op, file_or_fuse = __parse_memory_op(memory_op)
            parsed[memory] = [op, file_or_fuse]

    for memory in __memories:
        if memory not in parsed:
            parsed[memory] = None

    return parsed


def __test():
    parser = create_parser()
    args = "-p m16 -P /dev/ttyUSB0 -U flash:w:test.hex -U eeprom:w:eep.hex \
        -U hfuse:w:0xEA -U lock:w:5 -U lfuse:r:fuse.hex"

    parsed_args = parse(parser, args.split())

    for key in parsed_args:
        print(str(key) + ": " + str(parsed_args[key]))
