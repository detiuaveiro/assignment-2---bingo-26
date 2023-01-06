#!/bin/bash

function main()
{
    gnome-terminal \
    --tab -t "Playing Area" -e "bash -c 'python3 playing_area.py; exec bash'" --active \
    --tab -t "Caller" -e "bash -c 'python3 caller.py -n caller; exec bash'" \
    --tab -t "Player1" -e "bash -c 'python3 player.py -n p1; exec bash'" \
    --tab -t "Player2" -e "bash -c 'python3 player.py -n p2; exec bash'" \
    --tab -t "Player3" -e "bash -c 'python3 player.py -n p3; exec bash'"
    exit 0
}

main "$@" >/dev/null 2>&1