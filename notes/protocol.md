
msg = {
    "type": type,
    "data": data,
}

type:

- disqualify
    data = {
        "seq": int,
        "target_seq": int,
        "reason": str,
    }

- get_logs
    data = {
        "seq": int,
    }

- logs_response
    data = {
        "logs": [],
    }


- join 
    data = { 
        "client": "player" | "caller",
        "nickname": str,
        "public_key": str,
    }

- join_response
    data = { 
        "accepted": bool,
        "seq": int
    }

- ready
    data = {
        "seq": int,
    }

- ready_response
    data = {
        "players": [],
    }

- start
    data = {
        "seq": int,
        "players": [],
    }

- card
    data = {
        "seq": int,
        "card": [],
    }

- deck
    data = {
        "seq": int,
        "deck": [],
    }
    

- final_deck
    data = {
        "seq": int,
        "deck": [],
    }

- key
    data = {
        "seq": int,
        "key": list(str, str)
    }

- keys_response
    data = {
        "keys": {},
    }

- winners
    data = {
        "seq": int,
        "winners": [],
    }

- final_winners
    data = {
        "seq": int,
        "winners": [],
    }