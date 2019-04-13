class RuntimeException(Exception):
    pass


class JinjaTemplateError(RuntimeException):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return f"JinjaTemplateError: {self.message}"


class SqlLintError(RuntimeException):
    def __init__(self, message, temp_file_path):
        self.message = message
        self.temp_file_path = temp_file_path

    def __str__(self):
        return f"SqlLintError: {self.message}"
