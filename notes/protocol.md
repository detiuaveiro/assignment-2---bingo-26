
msg = {
    "type": "...", 
    "data": {...}
}

type:

- join 
    data = { 
        "client": "player" | "caller",
        "nickname": "...",
        "public_key": "..."
    }

- join_response
    data = { 
        "accepted": True/False 
    }

- start
    data = {}

- start_response
    data = {
        "num_players": ...,
    }

- card
    data = {
        "card": ...,
    }

- deck
    data = {
        "deck": ...,
    }

- winner
    data = {
        "winner": ...,
    }