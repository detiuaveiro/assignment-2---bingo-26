from src.User import User

class Caller(User):
    def __init__(self, parea_host, parea_port):
        super().__init__(parea_host, parea_port)   
        # - nickname
        # - random asymmetric key pair, generated just before their registration
        #     - the private key is used to sign the player’s messages
        #     - the public key is made available in the player profile
        # - The Citizen Card authentication key pair
        # - a random deck with N unique numbers

        # join the game
        self.proto.join(self.sock, "caller")

        self.handlers = {
            "join_response": self.join_response,
        } 
