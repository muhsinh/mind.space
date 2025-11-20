#!/bin/bash
set -e

echo ">>> [1/4] Updating System..."
apt-get update && apt-get install -y python3-pip python3-venv git tmux htop

echo ">>> [2/4] Creating Virtual Environment..."
python3 -m venv venv
source venv/bin/activate

echo ">>> [3/4] Installing Dependencies..."
# UPGRADE pip first
pip install --upgrade pip
# Force upgrade transformers for DeepSeek R1 support
pip install vllm openai rich tqdm pandas huggingface-hub
pip install --upgrade transformers

echo ">>> [4/4] Setup Complete."
echo ">>> IMPORTANT: Run 'huggingface-cli login' now."
