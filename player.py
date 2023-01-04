import argparse
from src.Player import Player

args = argparse.ArgumentParser()
args.add_argument('--addr', type=str, help='Player Area IP address', metavar='ADDR', default='localhost')
args.add_argument('-p', '--port', type=int, default=5000, help='Playing Area port', metavar='PLAYER_AREA_PORT')
parsed_args = args.parse_args()

player = Player(parsed_args.addr, parsed_args.port)
print("Player trying to connect to playing area on port", parsed_args.port)
player.run()