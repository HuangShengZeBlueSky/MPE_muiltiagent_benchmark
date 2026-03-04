import os
import json
from spread_API import run_spread_game
from critic import run_critic
from optimizer import run_optimizer
from prompt.prompt_for_spread import get_navigation_hints

def get_current_policies(policies_file, n_agents):
    if not os.path.exists(policies_file):
        initial_policies = {f"agent_{i}": get_navigation_hints() for i in range(n_agents)}
        with open(policies_file, "w", encoding="utf-8") as f:
            json.dump(initial_policies, f, indent=2, ensure_ascii=False)
        return initial_policies
        
    with open(policies_file, "r", encoding="utf-8") as f:
        return json.load(f)

def run_pipeline(provider="qwen", generations=5, n_agents=3):
    os.makedirs("results/llm_mappo", exist_ok=True)
    
    policies_file = "results/llm_mappo/current_policies.json"
    
    for gen in range(generations):
        print(f"\n{'='*20} LLM-MAPPO GENERATION {gen} {'='*20}")
        
        agent_policies = get_current_policies(policies_file, n_agents)
        
        # 1. Rollout (Data Collection)
        print("\n--- Phase 1: Rollout ---")
        video_file = f"results/llm_mappo/gen_{gen}_demo.mp4"
        log_file = f"results/llm_mappo/gen_{gen}_demo.json" # automatically created by spread_API.py
        
        # run game
        run_spread_game(
            provider=provider,
            output_file=video_file,
            N=n_agents,
            agent_policies=agent_policies
        )
        
        # 2. Critic Evaluation
        print("\n--- Phase 2: Centralized Critic Evaluation ---")
        critic_file = f"results/llm_mappo/gen_{gen}_critic.json"
        
        run_critic(log_file, provider=provider, output_file=critic_file)
        
        # 3. Optimizer Meta-Prompting
        print("\n--- Phase 3: Prompt Optimizer (Gradient Step) ---")
        new_policies_file = f"results/llm_mappo/gen_{gen}_new_policies.json"
        
        run_optimizer(
            critic_feedback_file=critic_file,
            current_policies_file=policies_file,
            provider=provider,
            output_file=new_policies_file
        )
        
        # 4. Version Control (Replace current policies with new policies for next generation)
        print("\n--- Phase 4: Version Control Commit ---")
        # In a real heavy system we'd parse performance, and perhaps reject the update if it scored horribly.
        # But for LLM-MAPPO AutoPE, we will overwrite `current_policies.json`.
        if os.path.exists(new_policies_file):
            with open(new_policies_file, "r", encoding="utf-8") as f:
                new_pol = json.load(f)
            with open(policies_file, "w", encoding="utf-8") as f:
                json.dump(new_pol, f, indent=2, ensure_ascii=False)
            print("Successfully updated policies for the next generation.")
        else:
            print("Warning: new policies not generated. Sticking with old policies.")

if __name__ == "__main__":
    # Choose your LLM explicitly here
    run_pipeline(provider="qwen", generations=3, n_agents=3)
