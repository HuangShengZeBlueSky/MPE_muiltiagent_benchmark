import os
import json
import time
from benchmark_runner import run_benchmark

# Models specified by the user
MODELS = [
    "minimax-m2.5",
    "glm-5",
    "gemini-3-flash",
    "qwen3.5-397b-a17b"
]

# All 9 MPE environments
ENVIRONMENTS = [
    "spread", "adversary", "tag"
]

NUM_EPISODES = 10
FIXED_SEED_START = 1
BASE_OUT_DIR = "results/batch_benchmarks"

def main():
    os.makedirs(BASE_OUT_DIR, exist_ok=True)
    
    # Structure to hold all the results
    all_results = {}
    
    start_time = time.time()
    
    for model in MODELS:
        print(f"\n{'='*60}")
        print(f"🚀 STARTING EVALUATION FOR MODEL: {model}")
        print(f"{'='*60}\n")
        
        all_results[model] = {}
        model_out_dir = os.path.join(BASE_OUT_DIR, model)
        os.makedirs(model_out_dir, exist_ok=True)
        
        for env in ENVIRONMENTS:
            print(f"\n--- Running Env: {env} | Model: {model} | Episodes: {NUM_EPISODES} ---")
            
            try:
                # We use provider='zaiwen' because it's configured in utils_api.py to accept custom model_name
                # and point to the unified API. If API key is missing, it will use ZAIWEN_API_KEY from env.
                result = run_benchmark(
                    env_name=env,
                    provider="zaiwen",
                    episodes=NUM_EPISODES,
                    output_dir=model_out_dir,
                    seed_start=FIXED_SEED_START,
                    model_name=model
                )
                
                # Extract relevant stats
                all_results[model][env] = {
                    "mean_reward": result.get("mean_reward"),
                    "std_reward": result.get("std_reward"),
                    "episodes": result.get("episodes")
                }
            except Exception as e:
                print(f"❌ Error running {env} with {model}: {str(e)}")
                all_results[model][env] = {
                    "error": str(e)
                }
                
            # Save partial summary after each environment to avoid losing data
            summary_path = os.path.join(BASE_OUT_DIR, "summary.json")
            with open(summary_path, "w", encoding="utf-8") as f:
                json.dump(all_results, f, indent=4, ensure_ascii=False)
                
    end_time = time.time()
    print("\n" + "="*60)
    print(f"✅ ALL BATCH BENCHMARKS COMPLETED in {end_time - start_time:.2f} seconds!")
    print(f"Results saved to {summary_path}")
    print("="*60)

if __name__ == "__main__":
    main()
