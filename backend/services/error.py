class CustomError(Exception):
    """Custom exception class to handle errors in the application."""
    
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code

    def __str__(self):
        return f"Error: {self.message} (status code: {self.status_code})"
