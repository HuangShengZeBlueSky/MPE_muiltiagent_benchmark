import os
import json
import time
import numpy as np
from collections import defaultdict
from spread_API import run_spread_game
from prompt.prompt_for_spread import get_navigation_hints

# Load env variables explicitly
try:
    from dotenv import load_dotenv
    load_dotenv(verbose=False)
except ImportError:
    pass

# Experimental configurations
EXP_CONFIGS = {
    "zero_shot": {
        "description": "Baseline: Static basic prompt, NO communication field supplied.",
        "use_comm": False,
        "use_evolution": False
    },
    "static_comm": {
        "description": "Static prompt but WITH communication field (no optimizer).",
        "use_comm": True,
        "use_evolution": False
    },
    "full_llm_mappo": {
        "description": "Full LLM-MAPPO: Communication + Critic + Optimizer evolution.",
        "use_comm": True,
        "use_evolution": True
    }
}

TRAIN_EPISODES_PER_GEN = 3 # Number of rollouts for critic to sample from per generation
GENERATIONS = 3      # If evolution is on, how many generations to run
TEST_SEEDS = list(range(1, 3)) # Fixed seeds for the final Test Eval (1 to 10)
N_AGENTS = 3
LOCAL_RATIO = 0.5

# Here you can map specific agents to specific APIs/Models
PROVIDER_CONFIG = {
    "agent_0": "gemini",
    "agent_1": "gemini",
    "agent_2": "gemini"
}

BASE_DIR = "results/experiments"

def extract_metrics(log_file):
    """Parse a game log JSON and extract standardized metrics."""
    if not os.path.exists(log_file):
        return None
        
    with open(log_file, "r", encoding="utf-8") as f:
        log_data = json.load(f)
        
    final_summary = None
    collisions = 0
    total_steps = 0
    
    for entry in log_data:
        if "final_summary" in entry:
            final_summary = entry
            continue
            
        total_steps = max(total_steps, entry["step"])
        
        # Count collisions from semantic feedback
        fb = entry.get("semantic_feedback", "")
        if "CRITICAL: Collided" in fb:
            collisions += 1
            
    # Since semantic feedback is per-agent, we divide by 2 for pairwise collisions loosely
    # Real collisions would be better counted from env infos, but this is a proxy.
    
    if final_summary:
        return {
            "mean_reward": final_summary.get("mean_reward", 0.0),
            "collisions_proxy": collisions,
            "steps": total_steps + 1
        }
    return None

def run_experiment_group(exp_name, config):
    print(f"\n{'='*50}")
    print(f"STARTING EXPERIMENT: {exp_name}")
    print(f"description: {config['description']}")
    print(f"{'='*50}\n")
    
    exp_dir = os.path.join(BASE_DIR, exp_name)
    os.makedirs(exp_dir, exist_ok=True)
    
    policies_file = os.path.join(exp_dir, "long_term_memories.json")
    
    # Initialize basic LTM
    initial_policies = {f"agent_{i}": "" for i in range(N_AGENTS)}
    with open(policies_file, "w", encoding="utf-8") as f:
        json.dump(initial_policies, f, indent=2, ensure_ascii=False)
        
    results = {}
    
    # ==========================================
    # PHASE 1: TRAINING / EVOLUTION
    # ==========================================
    gens_to_run = GENERATIONS if config["use_evolution"] else 1
    evolution_history = {}
    
    for gen in range(gens_to_run):
        print(f"\n--- [TRAIN PHASE] Generation {gen} ---")
        with open(policies_file, "r", encoding="utf-8") as f:
            agent_memories = json.load(f)
            
        evolution_history[f"gen_{gen}_ltm"] = agent_memories
        gen_metrics = []
        
        # Rollout Eval Phase for Critic
        for ep in range(TRAIN_EPISODES_PER_GEN):
            print(f"  -> Train Rollout {ep+1}/{TRAIN_EPISODES_PER_GEN}")
            video_file = os.path.join(exp_dir, f"train_gen_{gen}_ep_{ep}.mp4")
            log_file = os.path.join(exp_dir, f"train_gen_{gen}_ep_{ep}.json")
            
            try:
                run_spread_game(
                    provider=PROVIDER_CONFIG,
                    output_file=video_file,
                    N=N_AGENTS,
                    local_ratio=LOCAL_RATIO,
                    long_term_memories=agent_memories,
                    disable_comm=not config["use_comm"],
                    seed=gen * 100 + ep # Deterministic train seeds
                )
                
                metrics = extract_metrics(log_file)
                if metrics:
                    gen_metrics.append(metrics)
            except Exception as e:
                print(f"Error in train rollout: {e}")
                
        # Aggregate metrics for this train generation
        if gen_metrics:
            mean_rewards = [m["mean_reward"] for m in gen_metrics]
            avg_collisions = sum([m["collisions_proxy"] for m in gen_metrics]) / len(gen_metrics)
            print(f"  [Train Metrics] Avg Reward: {np.mean(mean_rewards):.3f} | Avg Collisions: {avg_collisions:.1f}")
        
        # Evolution Step (Critic -> Optimizer)
        if config["use_evolution"] and gen < gens_to_run:
            worst_ep_idx = np.argmin([m["mean_reward"] for m in gen_metrics]) if gen_metrics else 0
            worst_log = os.path.join(exp_dir, f"train_gen_{gen}_ep_{worst_ep_idx}.json")
            
            critic_file = os.path.join(exp_dir, f"train_gen_{gen}_critic.json")
            new_policies_file = os.path.join(exp_dir, f"train_gen_{gen}_optimized.json")
            
            if os.path.exists(worst_log):
                print("  -> Running Critic on worst rollout...")
                from critic import run_critic
                central_provider = list(PROVIDER_CONFIG.values())[0] if isinstance(PROVIDER_CONFIG, dict) else PROVIDER_CONFIG
                run_critic(worst_log, provider=central_provider, output_file=critic_file)
                
                print("  -> Running Optimizer to update LTM...")
                from optimizer import run_optimizer
                run_optimizer(critic_file, policies_file, provider=central_provider, output_file=new_policies_file)
                
                if os.path.exists(new_policies_file):
                    import shutil
                    shutil.copy(new_policies_file, policies_file)
                    print("  -> Long-Term Memory Updated for next generation.")
                    
    # Log evolution history
    with open(os.path.join(exp_dir, "evolution_history.json"), "w", encoding="utf-8") as f:
        json.dump(evolution_history, f, indent=2, ensure_ascii=False)
        
    # ==========================================
    # PHASE 2: TESTING / EVALUATION
    # ==========================================
    print(f"\n--- [TEST PHASE] Evaluating Final Strategy on 10 Fixed Seeds ---")
    with open(policies_file, "r", encoding="utf-8") as f:
        final_memories = json.load(f)
        
    test_metrics = []
    
    for seed in TEST_SEEDS:
        print(f"  -> Test Eval Seed: {seed}")
        video_file = os.path.join(exp_dir, f"test_seed_{seed}.mp4")
        log_file = os.path.join(exp_dir, f"test_seed_{seed}.json")
        
        try:
            run_spread_game(
                provider=PROVIDER_CONFIG,
                output_file=video_file,
                N=N_AGENTS,
                local_ratio=LOCAL_RATIO,
                long_term_memories=final_memories,
                disable_comm=not config["use_comm"],
                seed=seed # Hardcoded fixed seeds
            )
            
            metrics = extract_metrics(log_file)
            if metrics:
                test_metrics.append(metrics)
        except Exception as e:
            print(f"Error in test eval: {e}")
            
    if test_metrics:
        test_mean_rewards = [m["mean_reward"] for m in test_metrics]
        test_avg_collisions = sum([m["collisions_proxy"] for m in test_metrics]) / len(test_metrics)
        
        results["test_summary"] = {
            "avg_reward": np.mean(test_mean_rewards),
            "std_reward": np.std(test_mean_rewards),
            "avg_collisions": test_avg_collisions,
            "episodes_tested": len(test_metrics)
        }
        print(f"\n  *** [FINAL TEST RESULTS] Avg Reward: {np.mean(test_mean_rewards):.3f} | Avg Collisions: {test_avg_collisions:.1f} ***")
    
    # Save final aggregate results
    
    # Save final results
    with open(os.path.join(exp_dir, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
        
    return results

if __name__ == "__main__":
    all_experiments = {}
    for exp_name, config in EXP_CONFIGS.items():
        all_experiments[exp_name] = run_experiment_group(exp_name, config)
        
    # Super summary
    print("\n\n=== FINAL EXPERIMENT SUMMARY ===")
    print(json.dumps(all_experiments, indent=2))
    with open(os.path.join(BASE_DIR, "final_comparative_summary.json"), "w") as f:
        json.dump(all_experiments, f, indent=2)
