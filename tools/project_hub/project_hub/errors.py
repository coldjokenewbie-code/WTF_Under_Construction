class HubError(Exception):
    def __init__(self, code, error, status=400):
        super().__init__(error)
        self.code, self.status = code, status

    def payload(self):
        return {"error": str(self), "code": self.code}
