#!/bin/bash
# LAUNCHES 3 SPECIALIZED vLLM SERVERS ON H200
# 1. Qwen (Logic/Structure) -> Port 8000
# 2. DeepSeek VL (Chaos/Creative) -> Port 8001
# 3. DeepSeek R1 Llama (Writer/Instructor) -> Port 8002

source venv/bin/activate

# --- CONFIGURATION ---
# H200 has 141GB VRAM. 
# 0.3 (30%) per model = ~42GB each. 
# Total utilization = 90%. Ample room for context.
GPU_UTIL=0.3 
CTX_LEN=32768

# --- MODEL DEFINITIONS ---
MODEL_LOGIC="Qwen/Qwen2.5-7B-Instruct"
MODEL_CHAOS="deepseek-ai/deepseek-vl-7b-chat"
MODEL_WRITER="deepseek-ai/DeepSeek-R1-Distill-Llama-8B"

echo ">>> [1/3] Launching LOGIC ENGINE (Qwen) on Port 8000..."
nohup python3 -m vllm.entrypoints.openai.api_server \
    --model $MODEL_LOGIC \
    --port 8000 \
    --gpu-memory-utilization $GPU_UTIL \
    --max-model-len $CTX_LEN \
    --served-model-name logic-model \
    --trust-remote-code > logic.log 2>&1 &

echo ">>> [2/3] Launching CHAOS ENGINE (DeepSeek VL) on Port 8001..."
nohup python3 -m vllm.entrypoints.openai.api_server \
    --model $MODEL_CHAOS \
    --port 8001 \
    --gpu-memory-utilization $GPU_UTIL \
    --max-model-len $CTX_LEN \
    --served-model-name chaos-model \
    --trust-remote-code > chaos.log 2>&1 &

echo ">>> [3/3] Launching WRITER ENGINE (DeepSeek R1 Llama) on Port 8002..."
nohup python3 -m vllm.entrypoints.openai.api_server \
    --model $MODEL_WRITER \
    --port 8002 \
    --gpu-memory-utilization $GPU_UTIL \
    --max-model-len $CTX_LEN \
    --served-model-name writer-model \
    --trust-remote-code > writer.log 2>&1 &

echo ">>> Servers launching in background."
echo ">>> Monitor logs with: tail -f logic.log chaos.log writer.log"
echo ">>> Wait ~2-3 minutes for all ports to be active."