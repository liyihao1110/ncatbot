class CLIExit(Exception):
    def __init__(self, message: str = "CLI 退出"):
        self.message = message
        super().__init__(self.message)
