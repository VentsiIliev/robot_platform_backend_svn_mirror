#!/usr/bin/env bash
# run-ethercat.sh
# Opens a terminal window and runs the polling loop there (shows output live).

LOOP='while true; do clear; ethercat slaves; sleep 1; done'

# Try common terminal emulators in order
if command -v gnome-terminal >/dev/null 2>&1; then
    gnome-terminal -- bash -ic "$LOOP"
elif command -v konsole >/dev/null 2>&1; then
    # --noclose keeps konsole open when the command finishes (loop never ends anyway)
    konsole --noclose -e bash -ic "$LOOP"
elif command -v xfce4-terminal >/dev/null 2>&1; then
    xfce4-terminal --hold -e "bash -ic '$LOOP'"
elif command -v mate-terminal >/dev/null 2>&1; then
    mate-terminal -- bash -ic "$LOOP"
elif command -v xterm >/dev/null 2>&1; then
    xterm -hold -e "bash -ic '$LOOP'"
else
    # Fallback: run in the current terminal (no new window)
    echo "No supported graphical terminal found — running in the current terminal."
    bash -ic "$LOOP"
fi

