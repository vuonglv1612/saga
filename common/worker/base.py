class Worker:
    def __init__(self):
        self.callbacks = {}

    def register_callback(self, message_type, callback):
        self.callbacks[message_type] = callback

    def handle_message(self, message):
        message_type = message.get("type")
        if message_type in self.callbacks:
            self.callbacks[message_type](message)
        else:
            print("No callback registered for message type: " + message_type)

    def start(self):
        raise NotImplementedError()
