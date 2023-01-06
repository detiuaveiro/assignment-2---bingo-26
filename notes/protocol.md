
msg = {
    "type": "...", 
    "data": {...}
}

type:

- disqualify
    data = {
        "seq": ...,
        "reason": "..."
    }

- get_logs
    data = {}

- logs_response
    data = {
        "logs": "..."
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

- start
    data = {}

- start_response
    data = {
        "num_players": int,
    }

- card
    data = {
        "card": [],
    }

- deck
    data = {
        "deck": [],
    }

- final_deck
    data = {
        "deck": [],
    }

- get_keys
    data = {}

- keys_response
    data = {
        "keys": [],
    }

- winners
    data = {
        "seq": int,
        "winners": [],
    }

- final_winners
    data = {
        "winners": [],
    }