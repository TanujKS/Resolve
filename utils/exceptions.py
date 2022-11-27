class BillException(Exception):
    pass

class NoSummary(BillException):
    pass

class NoBill(BillException):
    pass

class NoText(BillException):
    pass

class RateLimited(Exception):
    pass

class TextTooLarge(Exception):
    pass

class EmbeddingError(Exception):
    pass
