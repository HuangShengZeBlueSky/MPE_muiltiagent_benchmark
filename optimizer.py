import os
import re
import json
from typing import Dict, Any

from utils_api import get_api_engine
from prompt.prompt_for_optimizer import get_optimizer_system_prompt, format_optimizer_input

def run_optimizer(critic_feedback_file: str, current_ltm_file: str, provider: str = "qwen", output_file: str = "optimized_ltm.json", **kwargs):
    """
    Run the Optimizer LLM on Critic Feedback to rewrite policies (Long-Term Memories).
    """
    if not os.path.exists(critic_feedback_file):
        print(f"Error: Feedback file {critic_feedback_file} not found.")
        return
        
    with open(critic_feedback_file, "r", encoding="utf-8") as f:
        critic_feedback = json.load(f)
        
    if not os.path.exists(current_ltm_file):
        print(f"Error: Current LTM file {current_ltm_file} not found.")
        return
        
    with open(current_ltm_file, "r", encoding="utf-8") as f:
        current_ltm = json.load(f)
        
    llm_engine = get_api_engine(provider, **kwargs)
    system_prompt = get_optimizer_system_prompt()
    
    new_memories = {}
    
    # Identify which agents have feedback
    feedback_agents = set([f["faulty_agent"] for f in critic_feedback.get("credit_assignment", [])])
    
    for agent_id, current_memory in current_ltm.items():
        if agent_id not in feedback_agents:
            new_memories[agent_id] = current_memory # No change
            continue
            
        print(f"Sending Optimizer request for {agent_id}...")
        text_observation = format_optimizer_input(current_memory, critic_feedback, agent_id)
        
        # Call LLM
        action_vec, response_text = llm_engine.generate_action(system_prompt, text_observation, temperature=0.5)
        
        try:
            clean_text = response_text.split("</think>")[-1] if "</think>" in response_text else response_text
            match = re.search(r'```json\s*(\{.*?\})\s*```', clean_text, re.DOTALL)
            if hasattr(match, "group"):
                json_str = match.group(1)
            else:
                match = re.search(r'(\{.*?\})', clean_text, re.DOTALL)
                if match:
                    json_str = match.group(1)
                else:
                    json_str = clean_text # Fallback

            parsed_opt = json.loads(json_str)
            new_memory_string = parsed_opt.get("new_policy_prompt", current_memory)
            print(f"Successfully optimized {agent_id}: {parsed_opt.get('change_log', 'Unknown changes')}")
            new_memories[agent_id] = new_memory_string
            
        except Exception as e:
            print(f"Failed to parse Optimizer JSON for {agent_id}. Keeping old memory. Error: {e}")
            new_memories[agent_id] = current_memory
            
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(new_memories, f, indent=2, ensure_ascii=False)
        
    print(f"Updated LTM structured and saved to {output_file}")
    
if __name__ == "__main__":
    # This module handles the execution of run_optimizer for the LTM module
    pass
