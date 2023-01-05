from src.User import User
import random

class Caller(User):
    def __init__(self, nickname, parea_host, parea_port):
        super().__init__(nickname, parea_host, parea_port)
        # Join playing area as caller
        self.proto.join(self.sock, "caller")

        self.handlers = {
            "join_response": self.handle_join_response,
        }
        self.deck = random.sample(range(1, 100), 100)
