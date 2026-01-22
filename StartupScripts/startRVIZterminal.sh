#!/usr/bin/env bash

# Command to run inside the new terminal
CMD='bash ~/Desktop/StartRVIZ.sh; echo; echo "Press ENTER to close..."; read'

if command -v gnome-terminal >/dev/null 2>&1; then
    gnome-terminal -- bash -c "$CMD"
elif command -v konsole >/dev/null 2>&1; then
    konsole --noclose -e bash -c "$CMD"
elif command -v xfce4-terminal >/dev/null 2>&1; then
    xfce4-terminal --hold -e "bash -c '$CMD'"
elif command -v mate-terminal >/dev/null 2>&1; then
    mate-terminal -- bash -c "$CMD"
elif command -v xterm >/dev/null 2>&1; then
    xterm -hold -e "bash -c \"$CMD\""
else
    echo "No supported terminal found — running in current shell."
    bash -c "$CMD"
fi

