# Documentação
## Estrutura do projeto
```
.
├── src
│   ├── __init__.py
│   ├── BingoProtocol.py -------->
│   ├── Caller.py --------------->
│   ├── CitizenCard.py ---------->
│   ├── CryptoUtils.py ---------->
│   ├── Player.py --------------->
│   ├── PlayingArea.py ---------->
│   ├── run.sh ------------------>
│   └── User.py ----------------->
├── caller.py ------------------->
├── player.py ------------------->
├── playing_area.py ------------->
└── requirements.txt ------------>
```

## Comunicação entre os módulos
![](img_link)

## Arranque
**User**: Player ou Caller
```mermaid
sequenceDiagram
    participant User
    participant PlayingArea
    User->>PlayingArea: join <br> ===================== <br> client: "player" | "caller",<br> nickname: str ,<br> public_key: str 
    PlayingArea-->>User: join_response <br> ===================== <br> accepted: bool,<br> seq: int, <br> public_key: str
```



# Créditos
| Nº mec. | Nome |
|--|--|
| 102534 | Rafael Gonçalves |
| 102536 | Leonardo Almeida |
| 102778 | Pedro Rodrigues |
| 103740 | Anzhelika Tosheva |
