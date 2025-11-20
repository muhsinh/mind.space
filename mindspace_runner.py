import json
import re
import os
import time
from datetime import datetime
from openai import OpenAI
from prompts import PROMPTS
from rich.console import Console
from rich.progress import track

# --- CONFIGURATION ---
console = Console()

# DEFINE THE 3 BRAINS
# Logic = Qwen (Port 8000)
# Chaos = DeepSeek VL (Port 8001)
# Writer = DeepSeek Llama (Port 8002)

CLIENTS = {
    "LOGIC":  OpenAI(base_url="http://localhost:8000/v1", api_key="EMPTY"), 
    "CHAOS":  OpenAI(base_url="http://localhost:8001/v1", api_key="EMPTY"), 
    "WRITER": OpenAI(base_url="http://localhost:8002/v1", api_key="EMPTY")  
}

MODELS = {
    "LOGIC":  "logic-model",
    "CHAOS":  "chaos-model",
    "WRITER": "writer-model"
}

INPUT_FILE = "scenarios.jsonl"
OUTPUT_FILE = "mindspace_results.jsonl"

# --- HELPER FUNCTIONS ---
def clean_json(text):
    if not text: return None
    try:
        return json.loads(text)
    except:
        match = re.search(r'```json\s*({.*?})\s*```', text, re.DOTALL)
        if match: return json.loads(match.group(1))
        match = re.search(r'({.*})', text, re.DOTALL)
        if match: return json.loads(match.group(1))
        return None

def call_model(brain_key, system_prompt, user_input, temperature=0.7, json_mode=False):
    client = CLIENTS[brain_key]
    model_name = MODELS[brain_key]
    
    # Safety check for empty inputs
    if not user_input or not isinstance(user_input, str):
        console.print(f"[red]Error: Invalid input sent to {brain_key} (None or empty)[/red]")
        return None

    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ],
            temperature=temperature,
            max_tokens=2048,
            response_format={"type": "json_object"} if json_mode else None
        )
        return response.choices[0].message.content
    except Exception as e:
        console.print(f"[bold red]Error on {brain_key}:[/bold red] {e}")
        return None

# --- PIPELINE ---
def run_pipeline(scenario):
    # 1. Robust Input Extraction
    # Tries 'input', then 'prompt', then 'text' to handle various JSONL formats
    user_input = scenario.get("input") or scenario.get("prompt") or scenario.get("text")
    s_id = scenario.get("id", "unknown")

    if not user_input:
        console.print(f"[bold red]>>> Skipping {s_id}: No valid input text found.[/bold red]")
        return None

    console.print(f"\n[bold blue]>>> Scenario {s_id}[/bold blue]")

    # 2. PRE-ACTION DEBATE
    console.print("   [yellow]1. Debate (Writer vs Chaos)...[/yellow]")
    prop = call_model("WRITER", PROMPTS["PROPONENT"], f"Input: {user_input}")
    opp  = call_model("CHAOS",  PROMPTS["OPPONENT"],  f"Input: {user_input}")

    # Moderator (Logic)
    console.print("   [yellow]2. Moderator (Logic)...[/yellow]")
    mod_ctx = f"User Input: {user_input}\n\nSafety View: {prop}\nPermissive View: {opp}"
    mod_raw = call_model("LOGIC", PROMPTS["MODERATOR"], mod_ctx, json_mode=True)
    
    if not mod_raw:
        console.print("[red]Aborting: Moderator failed.[/red]")
        return None

    mod_json = clean_json(mod_raw) or {"do": [], "dont": []}
    
    # Format Constraints
    do_txt = "\n".join([f"- Do: {x}" for x in mod_json.get("do", [])])
    dont_txt = "\n".join([f"- Don't: {x}" for x in mod_json.get("dont", [])])
    constraints = f"{do_txt}\n{dont_txt}"

    # 3. TARGET EXECUTION
    # Target (Writer)
    console.print("   [green]3. Target Response (Writer)...[/green]")
    target_sys = PROMPTS["TARGET_SYSTEM"].format(constraints=constraints)
    target_resp = call_model("WRITER", target_sys, user_input)

    if not target_resp:
        console.print("[red]Aborting: Target failed to generate response.[/red]")
        return None

    # 4. AUDIT
    # Auditor (Chaos)
    console.print("   [red]4. Auditor Probe (Chaos)...[/red]")
    audit_ctx = f"User: {user_input}\nTarget: {target_resp}"
    probe = call_model("CHAOS", PROMPTS["AUDITOR"], audit_ctx)

    # 5. EVALUATION
    console.print("   [magenta]5. Evaluation (Writer & Logic)...[/magenta]")
    full_log = f"USER: {user_input}\nTARGET: {target_resp}\nPROBE: {probe}"
    
    deb_a = call_model("WRITER", PROMPTS["DEBATER_A"], full_log)
    deb_b = call_model("WRITER", PROMPTS["DEBATER_B"], full_log)

    ref_in = f"TRANSCRIPT:\n{full_log}\n\nANALYSIS A: {deb_a}\nANALYSIS B: {deb_b}"
    ref_raw = call_model("LOGIC", PROMPTS["REFEREE"], ref_in, json_mode=True)
    judge_raw = call_model("LOGIC", PROMPTS["JUDGE"], full_log, json_mode=True)

    run_time = datetime.now().isoformat()

    return {
        "id": s_id,
        "timestamp": run_time,
        "input": user_input,
        "debate": {"proponent": prop, "opponent": opp, "moderator": mod_json},
        "interaction": {"response": target_resp, "probe": probe},
        "eval": {"referee": clean_json(ref_raw), "judge": clean_json(judge_raw)}
    }

def main():
    if not os.path.exists(INPUT_FILE):
        console.print(f"[red]Error: {INPUT_FILE} not found[/red]")
        return

    scenarios = []
    with open(INPUT_FILE, 'r') as f:
        for line in f:
            if line.strip():
                try:
                    scenarios.append(json.loads(line))
                except:
                    console.print("[yellow]Warning: Skipping invalid JSON line[/yellow]")
    
    with open(OUTPUT_FILE, 'a') as f_out:
        for sc in track(scenarios, description="Running Pipeline"):
            data = run_pipeline(sc)
            if data:
                f_out.write(json.dumps(data) + "\n")
                f_out.flush()

if __name__ == "__main__":
    main()
