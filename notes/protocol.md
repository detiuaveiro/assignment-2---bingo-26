
msg = {
    "type": "...", 
    "data": {...}
}

type:
- join 
    data = { 
        "client": "player" | "caller", 
        "host": "host", 
        "port": port 
    }

- join_response
    data = { 
        "accepted": True/False 
    }

