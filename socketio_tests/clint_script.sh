#!/bin/bash

taskset -c 0 python3 socketio_client.py & taskset -c 0 python3 socketio_client.py
