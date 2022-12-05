import pickle
from socket import socket

class Message:
    """Message Type."""
    def __init__(self, command):
        self.command = command
    def __repr__(self):
        return pickle.dumps({"command": self.command})
    
class JoinMessage(Message):
    """Message to join a chat channel."""
    def __init__(self, channel):
        super().__init__("join")
        self.channel = channel
    def __repr__(self):
        return  pickle.dumps({"command" : self.command, "channel" : self.channel})

class RegisterMessage(Message):
    """Message to register username in the server."""
    def __init__(self, user):
        super().__init__("register")
        self.user = user 
    def __repr__(self):
        return pickle.dumps({"command" : self.command, "user" : self.user}) 

class TextMessage(Message):
    """Message to chat with other clients."""
    def __init__(self, message):
        super().__init__("message")
        self.message = message
    def __repr__(self):
        return pickle.dumps({"command": self.command, "message": self.message})

class BingoProtocol:

    @classmethod
    def register(cls, username: str) -> RegisterMessage:
        """Creates a RegisterMessage object."""
        return  RegisterMessage(username)

    @classmethod
    def join(cls, channel: str) -> JoinMessage:
        """Creates a JoinMessage object."""
        return JoinMessage(channel)

    @classmethod
    def message(cls, message: str, channel: str = None) -> TextMessage:
        """Creates a TextMessage object."""
        return TextMessage(message, channel)

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
            if "channel" not in keys: raise ProtoBadFormat(msgBytes)
            return JoinMessage(text["channel"])
        elif command == "register":
            if "user" not in keys: raise ProtoBadFormat(msgBytes)
            return RegisterMessage(text["user"])
        elif command == "message":
            if "message" not in keys: raise ProtoBadFormat(msgBytes)
            if "ts" not in keys: raise ProtoBadFormat(msgBytes)
            if "channel" in keys:
                return TextMessage(text["message"], text["channel"], int(text["ts"]))
            else:
                return TextMessage(text["message"], None, int(text["ts"]))


class ProtoBadFormat(Exception):
    """Exception when source message is not Proto."""

    def __init__(self, original_msg: bytes=None) :
        """Store original message that triggered exception."""
        self._original = original_msg

    @property
    def original_msg(self) -> str:
        """Retrieve original message as a string."""
        return self._original.decode("utf-8")