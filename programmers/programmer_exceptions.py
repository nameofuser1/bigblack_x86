
class ProgrammerBaseError(IOError):

    def __init__(self, m=""):
        super(ProgrammerBaseError, self).__init__(m)


class HardwareError(ProgrammerBaseError):
    """
    Raised if something is wrong with hardware, e.g. uart/spi fail
        etc.
    """
    def __init__(self, m=""):
        super(HardwareError, self).__init__(m)


class WrongPacketError(ProgrammerBaseError):
    """
    Raised if incoming packet is not that we wait for
    """
    def __init__(self, m=""):
        super(WrongPacketError, self).__init__(m)
