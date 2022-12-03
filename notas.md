# BINGO GAME 

## Entidades:
- Player
- Caller
- Playing Area

---

## Análise de cada entidade:

### Player

All players must have:
- unique sequence number starting from 1 (used on messages and log messages)
- nickname
- random asymmetric key pair, generated just before their registration
	- the private key is used to sign the player’s messages
	- the public key is made available in the player/caller profile
- The Citizen Card authentication key pair
- card with M unique numbers
- random symmetric key, generated before encrypting the deck and stored until being publicly disclosed
	

Card generation:
1. each player generates their own card (N/4 positions (for instance), with random unique numbers from 0 to N)
2. protect the card by means of a digital signature
3. commit the card to the caller and all players


When a player receive a card from other player:
1. check if the size of the card is valid 
2. check if has no repeated numbers
3. check if the signature is valid
4. develop more...

	
Players also have to check the callers behaviour:
- check the deck
- check if accepts invalid cards

After the caller has posted the deck:
1. get the deck from playing area
2. encrypt each number of the deck with the symmetric key
3. reshuffle the numbers
4. sign the deck
5. post the deck to the playing area
	
---
	
### Caller

The caller acts mostly as a user, only with different access control rules. 

The caller MUST be in the list of possible callers stored by the playing area.



The Caller must have:
- sequence number equal to 0
- nickname
- random asymmetric key pair, generated just before their registration
	- the private key is used to sign the player’s messages
	- the public key is made available in the player profile
- The Citizen Card authentication key pair
- a random deck with N unique numbers


It also:
- should sign the data from all users: seq, nick, publickey


When the caller receive a card from a player:
1. check if the size of the card is valid 
2. check if has no repeated numbers
3. check if the signature is valid
4. see more...
	
IF THE CARD IS INVALID, THE PLAYER SHOULD BE DISQUALIFIED BY THE CALLER!

Deck generation:
1. shuffle the N unique numbers
2. encrypt each number of the deck with the symmetric key
3. sign the deck with the caller’s private key
4. post the deck to the playing area

The power of caller:

- Upon the revelation of the encryption keys, the caller has the power to detect cheaters and disqualify them. 

- A caller has the power to abort a game upon detecting a wrong player signature that compromises the continuation of the game.
	
	
	
### Playing Area

The playing area will act as a "server" in the app:
- users (caller and players) will connect to it
- makes information available to all
- implements authentication and authorization
- when the game starts, it should not accept more players
- record all messages exchanged and actions executed (log format: `sequence, timestamp, hash(prev_entry), text, signature`)
- players and callers can request this log and audit the events


The Playing Area must have:
- A random, asymmetric key pair. Used to sign messages it originates.
- only one Caller
- list of citizens that can act as callers
- list of players (registration order is important)
- see more like all messages, etc.


