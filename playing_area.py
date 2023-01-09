import argparse
from src.PlayingArea import PlayingArea

args = argparse.ArgumentParser()
args.add_argument('-p', '--port', type=int, default=5000, help='Port to listen on', metavar='PORT')
PORT = args.parse_args().port

print("Playing area listening on port", PORT)
p = PlayingArea("localhost", PORT)
p.run()