#!/bin/bash

function main()
{
    SHELL=$1
    if [ $# -ne 1 ]; then
        SHELL="bash"
    fi
    echo $SHELL
    gnome-terminal \
    --tab -t "Playing Area" -e "$SHELL -c 'python3 playing_area.py; exec $SHELL'" --active \
    --tab -t "Caller" -e "$SHELL -c 'sleep 0.5;python3 caller.py -n caller; exec $SHELL'" \
    --tab -t "Player1" -e "$SHELL -c 'sleep 1;python3 player.py -n p1; exec $SHELL'" \
    --tab -t "Player2" -e "$SHELL -c 'sleep 1.5;python3 player.py -n p2; exec $SHELL'" \
    --tab -t "Player3" -e "$SHELL -c 'sleep 2;python3 player.py -n p3; exec $SHELL'"
    exit 0
}

source venv/bin/activate
main "$@" >/dev/null 2>&1