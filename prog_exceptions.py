class EmptyBufferException(Exception):

    def __init__(self, message):
        super(EmptyBufferException, self).__init__(message)


class TimeoutException(Exception):

    def __init__(self, message):
        super(TimeoutException, self).__init__(message)


class WrongPacketException(Exception):

    def __init__(self, message):
        super(WrongPacketException, self).__init__(message)


class InternalError(Exception):

    def __init__(self, message):
        super(InternalError, self).__init__(message)


class DeviceError(Exception):

    def __init__(self, message):
        super(DeviceError, self).__init__(message)