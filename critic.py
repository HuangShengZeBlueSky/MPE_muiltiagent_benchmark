import os
import re
import json
from typing import Dict, Any

from utils_api import get_api_engine
from prompt.prompt_for_critic import get_critic_system_prompt, format_trajectory_for_critic

def run_critic(log_file: str, provider: str = "qwen", output_file: str = "critic_feedback.json", **kwargs):
    """
    Run the Critic LLM on a given trajectory log.
    
    Args:
        log_file: Path to the JSON log output by spread_API.py
        provider: Model provider, e.g., 'qwen', 'deepseek', 'gpt'
        output_file: Where to save the Critic's text gradients
    """
    if not os.path.exists(log_file):
        print(f"Error: Log file {log_file} not found.")
        return
        
    with open(log_file, "r", encoding="utf-8") as f:
        game_log = json.load(f)
        
    print(f"Loaded game log with {len(game_log)} entries.")
    
    # 1. Format the data for the LLM
    text_observation = format_trajectory_for_critic(game_log)
    system_prompt = get_critic_system_prompt()
    
    # 2. Setup the LLM
    llm_engine = get_api_engine(provider, **kwargs)
    
    print("Sending trajectory to Critic LLM for analysis...")
    
    # Generate response
    # Re-use APIInferencer's base call for raw text (bypassing generate_action if we only want JSON string without actions)
    # The utils_api generate_action returns (action_vec, full_text). We ignore action_vec.
    action_vec, response_text = llm_engine.generate_action(system_prompt, text_observation, temperature=0.3)
    
    print("Critic response received. Parsing JSON...")
    
    # 3. Parse and extract JSON
    critic_json_str = ""
    try:
        clean_text = response_text.split("</think>")[-1] if "</think>" in response_text else response_text
        match = re.search(r'```json\s*(\{.*?\})\s*```', clean_text, re.DOTALL)
        if hasattr(match, "group"):
            critic_json_str = match.group(1)
        else:
            match = re.search(r'(\{.*?\})', clean_text, re.DOTALL)
            if match:
                critic_json_str = match.group(1)
            else:
                critic_json_str = clean_text # Fallback
        
        parsed_critic = json.loads(critic_json_str)
        
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(parsed_critic, f, indent=2, ensure_ascii=False)
            
        print(f"Critic analysis successfully saved to {output_file}")
        
    except json.JSONDecodeError as e:
        print(f"Failed to parse Critic JSON. Error: {e}")
        print("Raw response:")
        print(response_text)
        with open(output_file.replace(".json", "_raw.txt"), "w", encoding="utf-8") as f:
            f.write(response_text)
            
if __name__ == "__main__":
    # Example usage:
    # First run spread_API.py to generate a log, then point runtime to that log.
    run_critic("demo_qwen.json", provider="qwen")
