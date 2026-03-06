import os
import json
import time
import argparse
from benchmark_runner import run_benchmark

# Models specified by the user
MODELS = [
    #"kimi-k2.5",
    "GLM-5",
    #"Gemini-3.0-Flash",
    #"Qwen-3-Max"
    
]

# All 9 MPE environments
ENVIRONMENTS = [
    "adversary"
]

NUM_EPISODES = 6
FIXED_SEED_START = 4
BASE_OUT_DIR = "results/batch_benchmarks"

def parse_args():
    p = argparse.ArgumentParser(description="Run batch benchmarks across multiple models and MPE environments.")
    p.add_argument("--episodes", type=int, default=NUM_EPISODES)
    p.add_argument("--seed_start", type=int, default=FIXED_SEED_START)
    p.add_argument("--out_dir", type=str, default=BASE_OUT_DIR)
    p.add_argument("--provider", type=str, default="zaiwen")
    p.add_argument("--api_base", type=str, default=os.getenv("ZAIWEN_API_BASE"))
    p.add_argument("--api_key", type=str, default=os.getenv("ZAIWEN_API_KEY"))
    return p.parse_args()


def main():
    args = parse_args()

    if args.provider.lower() == "zaiwen":
        if not args.api_key:
            raise ValueError("Missing API key: set ZAIWEN_API_KEY in .env or pass --api_key")
        if not args.api_base:
            raise ValueError("Missing API base URL: set ZAIWEN_API_BASE in .env or pass --api_base")

    os.makedirs(args.out_dir, exist_ok=True)
    
    # Structure to hold all the results
    all_results = {}
    
    start_time = time.time()
    
    for model in MODELS:
        print(f"\n{'='*60}")
        print(f"🚀 STARTING EVALUATION FOR MODEL: {model}")
        print(f"{'='*60}\n")
        
        all_results[model] = {}
        model_out_dir = os.path.join(args.out_dir, model)
        os.makedirs(model_out_dir, exist_ok=True)
        
        for env in ENVIRONMENTS:
            print(f"\n--- Running Env: {env} | Model: {model} | Episodes: {args.episodes} ---")
            
            try:
                # We use provider='zaiwen' because it's configured in utils_api.py to accept custom model_name
                # and point to the unified API. If API key is missing, it will use ZAIWEN_API_KEY from env.
                benchmark_kwargs = {
                    "model_name": model,
                }
                if args.api_key:
                    benchmark_kwargs["api_key"] = args.api_key
                if args.api_base:
                    benchmark_kwargs["api_base"] = args.api_base

                result = run_benchmark(
                    env_name=env,
                    provider=args.provider,
                    episodes=args.episodes,
                    output_dir=model_out_dir,
                    seed_start=args.seed_start,
                    **benchmark_kwargs
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
            summary_path = os.path.join(args.out_dir, "summary.json")
            with open(summary_path, "w", encoding="utf-8") as f:
                json.dump(all_results, f, indent=4, ensure_ascii=False)
                
    end_time = time.time()
    print("\n" + "="*60)
    print(f"✅ ALL BATCH BENCHMARKS COMPLETED in {end_time - start_time:.2f} seconds!")
    print(f"Results saved to {summary_path}")
    print("="*60)

if __name__ == "__main__":
    main()
