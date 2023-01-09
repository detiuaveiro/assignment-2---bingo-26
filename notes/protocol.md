
msg = {
    "data": data,
    "signature": str
}

type:

- redirect
    data = {
        "type": "redirect",
        "msg": {
            "data": data (redirected),
            "signature": str
        }
    }

- disqualify
    data = {
        "type": "disqualify",
        "seq": int,
        "target_seq": int,
        "reason": str
    }

- get_logs
    data = {
        "type": "get_logs"
    }

- logs_response
    data = {
        "type": "logs_response",
        "logs": list
    }


- join 
    data = { 
        "type": "join",
        "client": "player" | "caller",
        "nickname": str,
        "public_key": str,
        "cc_public_key": str
    }

- join_response
    data = { 
        "type": "join_response",
        "accepted": bool,
        "seq": int,
        "parea_public_key": str
    }

- ready
    data = {
        "type": "ready",
        "seq": int
    }

- ready_response
    data = {
        "type": "ready_response",
        "players": list
    }

- start
    data = {
        "type": "start",
        "seq": int,
        "players": dict
    }

- card
    data = {
        "type": "card",
        "seq": int,
        "card": list
    }

- deck
    data = {
        "type": "deck",
        "seq": int,
        "deck": list
    }
    

- final_deck
    data = {
        "type": "final_deck",
        "seq": int,
        "deck": list
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
        "keys": list
    }

- winners
    data = {
        "type": "winners",
        "seq": int,
        "winners": list
    }

- final_winners
    data = {
        "type": "final_winners",
        "seq": int,
        "winners": list
    }