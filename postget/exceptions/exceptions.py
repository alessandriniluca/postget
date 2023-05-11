class WrongDateString(Exception):
    def __init__(self, format_received, format_requested):
        self.format_received = format_received
        self.format_requested = format_requested
        message = f'[postget]: You passed was {format_received}, whereas it is requested {format_requested}'
        super().__init__(message)

class NoTweetsReturned(Exception):
    def __init__(self, searchbox_input):
        message = f'[postget]: No tweets returned from the search \'{searchbox_input}\''
        super().__init__(message)

class ElementNotLoaded(Exception):
    def __init__(self, message):
        message = f'[postget]: {message}'
        super().__init__(message)