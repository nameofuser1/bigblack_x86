
class NetworkBaseError(IOError):
    """
    Base class for all network errors
    """

    def __init__(self, m=""):
        super(NetworkBaseError, self).__init__(m)


class NetworkTimeoutError(NetworkBaseError):
    """
    Raise if answer did not come
    """
    def __init__(self, m=""):
        super(NetworkTimeoutError, self).__init__(m)


class NetworkConnectionError(NetworkBaseError):
    """
    Raised if connection with esp was not established
    """
    def __init__(self, m=""):
        super(NetworkConnectionError, self).__init__(m)


class BrokenPacketError(NetworkBaseError):
    """
    Raised when it is impossible to parse packet
    """
    def __init__(self, m=""):
        super(BrokenPacketError, self).__init__(m)
