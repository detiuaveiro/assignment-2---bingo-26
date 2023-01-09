import argparse
from getpass import getpass
from src.Caller import Caller

args = argparse.ArgumentParser()
args.add_argument('-n', '--nickname', type=str, help='Player nickname', metavar='NICKNAME', default='caller')
args.add_argument('--addr', type=str, help='Player Area IP address', metavar='ADDR', default='localhost')
args.add_argument('-p', '--port', type=int, default=5000, help='Player Area port', metavar='PLAYER_AREA_PORT')
args.add_argument("-s", "--slot", type=int, default=0, help="Citizen Card slot", metavar="SLOT")
parsed_args = args.parse_args()

pin = getpass("Enter PIN: ")

print("Caller trying to connect to playing area on port", parsed_args.port)
caller = Caller(parsed_args.nickname, parsed_args.addr, parsed_args.port, pin, parsed_args.slot)
caller.run()