#!/bin/sh -x

# Start a server in a new process
python server.py 8889 &

# $! refers to the PID of the last process launched in the background
server_pid=$!

# Sleep for a bit so server has time to initialize everything
sleep 0.3

# Runt tests
node e2e-test.js 8889

# Kill the server process
kill $server_pid