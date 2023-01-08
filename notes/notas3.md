[x] When the game starts, the playing area shall not accept more players.

[ ] The playing area has a keypair which it uses to sign messages exchanged or forwarded.

[ ] All the messages produced by players must be signed by them, before being transmitted. 

[x] A user’s authentication process must ensure a commitment of the user public key and nickname.

[x] The caller should sign the data from all users (seq, nick, publickey)

[x] The card of each player is committed to the caller and to the other players, protected by means of a digital signature. 

[x] After all decks are provided, the caller will sign it again, making this deck the one to be considered for playing.

[x] Finally, all players and the caller provide their symmetric keys to all users.

[x] Upon all decryption steps, all players must reach the exact same shuffled version of the plaintext deck, which they must confirm that is signed by the caller.

[x] when a game starts, all the players, and the caller, know the public keys of all the players.