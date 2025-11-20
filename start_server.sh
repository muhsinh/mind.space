#!/bin/bash
# LAUNCHES 3 SPECIALIZED vLLM SERVERS ON H200
# 1. Logic: Qwen 2.5 7B
# 2. Chaos: DeepSeek Coder 6.7B
# 3. Writer: DeepSeek R1 Llama 8B

source venv/bin/activate

# --- CRITICAL STABILITY FLAGS ---
export VLLM_USE_V1=0                # Force Stable Engine (Fixes v1/core crash)
export VLLM_WORKER_MULTIPROC_METHOD=spawn # Fixes multiprocessing issues
GPU_UTIL=0.28                       # Lowered slightly for safety
CTX_LEN=32768

# --- MODEL DEFINITIONS ---
MODEL_LOGIC="Qwen/Qwen2.5-7B-Instruct"
MODEL_CHAOS="deepseek-ai/deepseek-coder-6.7b-instruct"
MODEL_WRITER="deepseek-ai/DeepSeek-R1-Distill-Llama-8B"

# --- 1. LOGIC ENGINE ---
echo ">>> [1/3] Launching LOGIC (Qwen) on Port 8000..."
nohup python3 -m vllm.entrypoints.openai.api_server \
    --model $MODEL_LOGIC \
    --port 8000 \
    --gpu-memory-utilization $GPU_UTIL \
    --max-model-len $CTX_LEN \
    --served-model-name logic-model \
    --enforce-eager \
    --trust-remote-code > logic.log 2>&1 &

echo ">>> Waiting 30s for Logic to initialize..."
sleep 30

# --- 2. CHAOS ENGINE ---
echo ">>> [2/3] Launching CHAOS (DeepSeek Coder) on Port 8001..."
nohup python3 -m vllm.entrypoints.openai.api_server \
    --model $MODEL_CHAOS \
    --port 8001 \
    --gpu-memory-utilization $GPU_UTIL \
    --max-model-len $CTX_LEN \
    --served-model-name chaos-model \
    --enforce-eager \
    --trust-remote-code > chaos.log 2>&1 &

echo ">>> Waiting 30s for Chaos to initialize..."
sleep 30

# --- 3. WRITER ENGINE ---
echo ">>> [3/3] Launching WRITER (DeepSeek R1) on Port 8002..."
nohup python3 -m vllm.entrypoints.openai.api_server \
    --model $MODEL_WRITER \
    --port 8002 \
    --gpu-memory-utilization $GPU_UTIL \
    --max-model-len $CTX_LEN \
    --served-model-name writer-model \
    --enforce-eager \
    --trust-remote-code > writer.log 2>&1 &

echo ">>> All servers launched."
echo ">>> Monitor logs with: tail -f logic.log chaos.log writer.log"
