class WrongDateString(Exception):
    def __init__(self, format_received, format_requested):
        self.format_received = format_received
        self.format_requested = format_requested
        message = f"You passed was {format_received}, whereas it is requested {format_requested}"
        super().__init__(message)