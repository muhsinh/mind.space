Mindspace 3-Model Engine on H200

This setup runs 3 specialized models concurrently on a single H200 GPU to execute the Mindspace alignment pipeline (Debate -> Constraints -> Target -> Audit).

Architecture

Port 8000 (Logic): Qwen 2.5 7B (Moderator, Referee, Judge)
Selected for: Structural adherence and JSON enforcement.

Port 8001 (Chaos): DeepSeek VL 7B (Opponent, Auditor)
Selected for: Creative probing and red-teaming.

Port 8002 (Writer): DeepSeek R1 Llama 8B (Target, Proponent, Debaters)
Selected for: Instruction following and coherent explanations.

Inputs & Outputs

Input: scenarios.jsonl (List of user prompts to test)

Output: mindspace_results.jsonl (Full JSON logs of the pipeline)

Instructions

Setup Environment:

chmod +x setup_env.sh start_server.sh
./setup_env.sh


Login to Hugging Face:
(Required for DeepSeek/Meta model access)

source venv/bin/activate
huggingface-cli login


Launch Servers:

./start_server.sh


Wait 2-3 minutes. Check logs with tail -f logic.log chaos.log writer.log.
Ensure you see "Uvicorn running on..." in all three logs.

Run Experiment:

python mindspace_runner.py
