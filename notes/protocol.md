
msg = {
    "type": "...", 
    "data": {...}
}

type:
- join 
    data = { 
        "client": "player" | "caller", 
    }

- join_response
    data = { 
        "accepted": True/False 
    }

