#!/usr/bin/env bash

FOLDER="./clevercart_env/"
CHROMEDRIVER="/usr/local/bin/chromedriver"

if [ -d "$FOLDER" ]; then
    source ./clevercart_env/bin/activate
else
    echo "Virtual Environment not found, creating and installing dependencies..."
    sudo apt update && sudo apt install -y python3 python3-venv
    python3 -m venv clevercart_env
    source ./clevercart_env/bin/activate
    python3 -m pip install flask flask-sqlalchemy flask-login user_agents gevent selenium openai
fi

python3 main.py