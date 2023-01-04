import argparse
from src.Caller import Caller

args = argparse.ArgumentParser()
args.add_argument('--addr', type=str, help='Player Area IP address', metavar='ADDR', default='localhost')
args.add_argument('-p', '--port', type=int, default=5000, help='Player Area port', metavar='PLAYER_AREA_PORT')
parsed_args = args.parse_args()

caller = Caller(parsed_args.addr, parsed_args.port)
print("Caller trying to connect to playing area on port", parsed_args.port)
caller.run()