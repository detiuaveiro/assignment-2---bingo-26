
msg = {
    "data": data,
    "signature": str,
}

type:

- redirect
    data = {
        "type": "redirect",
        "msg": msg,
    }

- disqualify
    data = {
        "type": "disqualify",
        "seq": int,
        "target_seq": int,
        "reason": str,
    }

- get_logs
    data = {
        "type": "get_logs",
        "seq": int,
    }

- logs_response
    data = {
        "type": "logs_response",
        "logs": [],
    }


- join 
    data = { 
        "type": "join",
        "client": "player" | "caller",
        "nickname": str,
        "public_key": str,
    }

- join_response
    data = { 
        "type": "join_response",
        "accepted": bool,
        "seq": int
    }

- ready
    data = {
        "type": "ready",
        "seq": int,
    }

- ready_response
    data = {
        "type": "ready_response",
        "players": [],
    }

- start
    data = {
        "type": "start",
        "seq": int,
        "players": [],
    }

- card
    data = {
        "type": "card",
        "seq": int,
        "card": [],
    }

- deck
    data = {
        "type": "deck",
        "seq": int,
        "deck": [],
    }
    

- final_deck
    data = {
        "type": "final_deck",
        "seq": int,
        "deck": [],
    }

- key
    data = {
        "type": "key",
        "seq": int,
        "key": list[str, str]
    }

- keys_response
    data = {
        "type": "keys_response",
        "keys": [[str, str], ...]]
    }

- winners
    data = {
        "type": "winners",
        "seq": int,
        "winners": [],
    }

- final_winners
    data = {
        "type": "final_winners",
        "seq": int,
        "winners": [],
    }