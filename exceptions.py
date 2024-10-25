class DoesNotExist(Exception):
    def __init__(self, subject):
        self.message = f"{subject} doesn't exist"
        super().__init__(self.message)


class NotSupplied(Exception):
    def __init__(self, subject):
        self.message = f"{subject} not supplied"
        super().__init__(self.message)