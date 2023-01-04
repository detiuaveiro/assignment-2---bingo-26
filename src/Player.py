from src.User import User
import random

class Player(User):
    def __init__(self, parea_host, parea_port):
        super().__init__(parea_host, parea_port)
        
        # All players must have:
        # - unique sequence number starting from 1 (used on messages and log messages)
        # - nickname
        # - random asymmetric key pair, generated just before their registration
        #     - the private key is used to sign the player’s messages
        #     - the public key is made available in the player/caller profile
        # - The Citizen Card authentication key pair
        # - card with M unique numbers
        # - random symmetric key, generated before encrypting the deck and stored until being publicly disclosed

        # join the game
        # join the game
        self.proto.join(self.sock, "player")

        self.handlers = {
            "join_response": self.join_response,
        }

        self.card = random.sample(range(1, 90-1), 18)