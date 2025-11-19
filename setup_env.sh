#!/bin/bash
set -e

echo ">>> [1/3] Updating System Packages..."
apt-get update && apt-get install -y python3-pip python3-venv git tmux htop

echo ">>> [2/3] Creating Virtual Environment..."
python3 -m venv venv
source venv/bin/activate

echo ">>> [3/3] Installing AI Dependencies (vLLM + OpenAI)..."
# Installing vLLM for the server and OpenAI for the client wrapper
pip install --upgrade pip
pip install vllm openai rich tqdm pandas

echo ">>> Setup Complete. Run 'source venv/bin/activate' to begin."