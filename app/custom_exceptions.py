class APIKeyError(Exception):
    def __init__(self, status_code, detail):
        self.status_code = status_code
        self.detail = detail


class EncodeError(Exception):
    def __init__(self, status_code, detail):
        self.status_code = status_code
        self.detail = detail


class SignatureError(Exception):
    def __init__(self, status_code, detail):
        self.status_code = status_code
        self.detail = detail
