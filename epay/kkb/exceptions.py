

class EpayError(Exception):
    pass


class RequestError(EpayError):
    pass


class VerificationError(EpayError):
    pass
