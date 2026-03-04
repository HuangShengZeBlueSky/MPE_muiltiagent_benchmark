import json

def get_critic_system_prompt() -> str:
    return (
        "You are an expert Multi-Agent Reinforcement Learning Critic with a 'God's eye' view. "
        "Your task is to analyze an episode's trajectory log to identify suboptimal behaviors and provide textual credit assignment (Textual Advantage). "
        "You will receive the full game log, including each agent's local observations, communications, actions, and step rewards/semantic feedback.\n\n"
        "CRITICAL RULES:\n"
        "1. Identify specifically which agent made an error at which step.\n"
        "2. If an agent ignored a teammate's message and collided, that is a Communication_Failure.\n"
        "3. Output MUST be strictly in the following JSON format wrapped in markdown blocks:\n\n"
        "```json\n"
        "{\n"
        '  "episode_analysis": "Brief summary of team performance (e.g., collisions, success).",\n'
        '  "credit_assignment": [\n'
        "    {\n"
        '      "faulty_agent": "agent_id",\n'
        '      "error_step": <integer>,\n'
        '      "error_type": "Collision / Target_Conflict / Communication_Failure / Inefficiency",\n'
        '      "advantage_analysis": "Detailed textual explanation of WHY the action was suboptimal and what the optimal policy/action should have been.",\n'
        '      "prompt_optimization_direction": "Concrete, actionable rule to add to the agent\'s prompt to fix this behavior in the future."\n'
        "    }\n"
        "  ]\n"
        "}\n"
        "```\n"
    )

def format_trajectory_for_critic(game_log: list) -> str:
    """Format the game log JSON down to the essentials so it fits in the LLM context."""
    summary = []
    
    final_summary = None
    steps_data = {}
    
    for entry in game_log:
        if "final_summary" in entry:
            final_summary = entry
            continue
            
        step = entry["step"]
        if step not in steps_data:
            steps_data[step] = []
        
        steps_data[step].append({
            "agent": entry["agent"],
            "action": entry["action"],
            "message": entry.get("message", ""),
            "feedback": entry.get("semantic_feedback", "")
        })
        
    prompt = "EPISODE TRAJECTORY SUMMARY:\n"
    if final_summary:
        prompt += f"Final Mean Reward: {final_summary.get('mean_reward', 0):.3f}\n"
        prompt += f"Total Agent Rewards: {json.dumps(final_summary.get('total_rewards', {}))}\n\n"
        
    for step in sorted(steps_data.keys()):
        prompt += f"--- Step {step} ---\n"
        for ag_data in steps_data[step]:
            short_action = [round(a, 2) for a in ag_data['action']]
            msg = ag_data['message']
            fb = ag_data['feedback']
            if not msg: msg = "None"
            prompt += f"  [{ag_data['agent']}] Action: {short_action} | Msg: '{msg}' | Feedback: {fb}\n"
            
    prompt += "\n"
    prompt += "Please identify the most critical errors (if any) and output the JSON."
    
    return prompt
