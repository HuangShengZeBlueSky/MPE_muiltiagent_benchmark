import json

def get_optimizer_system_prompt() -> str:
    return (
        "You are an expert Strategy Optimizer (Long-Term Memory Manager) for a Multi-Agent system. Your task is to update an Agent's Long-Term Memory (Abstract Skills/Protocols) based on feedback from a centralized Critic.\n\n"
        "CRITICAL RULES:\n"
        "1. Identify the 'prompt_optimization_direction' heavily requested by the Critic.\n"
        "2. The Agent already has a FIXED set of basic navigation rules (immutable). Your output will be appended as 'LONG-TERM MEMORY' to their prompt.\n"
        "3. You must rewrite the agent's current Long-Term Memory to incorporate the new abstract rules or negotiation protocols.\n"
        "4. Output MUST be strictly in the following JSON format wrapped in markdown blocks:\n\n"
        "```json\n"
        "{\n"
        '  "change_log": "A brief summary of what abstract skill you added/modified.",\n'
        '  "new_policy_prompt": "The complete, updated text for the Long-Term Memory block. This should ONLY contain advanced behavioral rules (e.g. negotiation/yielding), NOT basic physics."\n'
        "}\n"
        "```\n"
    )

def format_optimizer_input(current_prompt: str, critic_feedback: dict, agent_id: str) -> str:
    """Format the optimizer input incorporating current logic and feedback context."""
    
    agent_feedbacks = [f for f in critic_feedback.get("credit_assignment", []) if f["faulty_agent"] == agent_id]
    
    if not agent_feedbacks:
        return "" # No update needed for this agent
        
    feedback_str = "\n".join([f"- Step {f['error_step']} Error ({f['error_type']}):\n  Analysis: {f['advantage_analysis']}\n  Suggestion: {f['prompt_optimization_direction']}" for f in agent_feedbacks])
    
    prompt = (
        f"AGENT ID: {agent_id}\n\n"
        "--- CURRENT LONG-TERM MEMORY (Abstract Skills) ---\n"
        f"{current_prompt if current_prompt else '(Empty)'}\n\n"
        "--- CRITIC FEEDBACK (GRADIENTS) ---\n"
        f"{feedback_str}\n\n"
        "Based on the Critic Feedback, rewrite the CURRENT LONG-TERM MEMORY. "
        "Your new memory block should explicitly state the new coordination protocol or yielding rule exactly as required to fix the error."
    )
    
    return prompt
