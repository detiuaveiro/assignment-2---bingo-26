
user -> join -> playing_area
playing_area -> join_response -> user

caller -> start -> playing_area -> start -> all_players
all_players -> card -> playing_area -> card -> all_users
caller -> deck -> playing_area -> deck -> player
player -> deck -> playing_area -> deck -> player... until all players shuffled the deck
player -> deck -> playing_area -> deck -> caller
caller -> final_deck -> playing_area -> final_deck -> all_players
all_players -> winners -> playing_area -> winners -> caller