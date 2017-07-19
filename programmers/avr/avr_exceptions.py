from programmers.programmer_exceptions import ProgrammerBaseError


class AVRError(ProgrammerBaseError):
    """
    Base error class for AVR programmer
    """
    def __init__(self, m=""):
        super(AVRError, self).__init__(m)


class DeviceError(AVRError):
    """
    Raised if something is wrong with AVR
    For instance, things like entering pmg mode,
        wrong return for commands etc.
    """
    def __init__(self, m=""):
        super(DeviceError, self).__init__(m)


class InternalError(AVRError):
    """
    Used for programmer error checking. Means some software bug
    """

    def __init__(self, m=""):
        super(InternalError, self).__init__(m)


class ConfigParserError(AVRError):
    """
    Raise if something is wrong with parsing parts list
    """

    def __init__(self, m=""):
        super(ConfigParserError, self).__init__(m)
