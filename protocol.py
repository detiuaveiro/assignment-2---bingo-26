import pickle
from socket import socket

class Message:
    """Message Type."""
    def __init__(self, command):
        self.command = command
    def __repr__(self):
        return pickle.dumps({"command": self.command})
    
class JoinMessage(Message):
    """Message to join a game session."""
    def __init__(self, username):
        super().__init__("join")
        self.username = username
    def __repr__(self):
        return  pickle.dumps({"command" : self.command, "username" : self.username})

class BingoProtocol:

    @classmethod
    def join(cls, channel: str) -> JoinMessage:
        """Creates a JoinMessage object."""
        return JoinMessage(channel)

    @classmethod
    def send_msg(cls, connection: socket, msg: Message):
        """Sends through a connection a Message object."""
        text = str(msg)
        size = len(text).to_bytes(2, "big")
        connection.send(size + text.encode("utf-8"))

    @classmethod
    def recv_msg(cls, connection: socket) -> Message:
        """Receives through a connection a Message object."""
        size = int.from_bytes(connection.recv(2) , "big")
        if size == 0: return None
        msgBytes = connection.recv(size)
        text = msgBytes.decode("utf-8")
        try:
            text = pickle.loads(text)
        except:
            raise ProtoBadFormat(msgBytes)
        keys = text.keys()
        if "command" not in keys: raise ProtoBadFormat(msgBytes)
        command = text["command"]
        if command == "join":
            if "username" not in keys: raise ProtoBadFormat(msgBytes)
            return JoinMessage(text["username"])

class ProtoBadFormat(Exception):
    """Exception when source message is not Proto."""

    def __init__(self, original_msg: bytes=None) :
        """Store original message that triggered exception."""
        self._original = original_msg

    @property
    def original_msg(self) -> str:
        """Retrieve original message as a string."""
        return self._original.decode("utf-8")