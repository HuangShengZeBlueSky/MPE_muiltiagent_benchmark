import os
import json
import time
from benchmark_runner import run_benchmark

# User specified models
MODELS = [
    "minimax-m2.5",
    "glm-5",
    "gemini-3-flash",
    "qwen3.5-397b-a17b"
]

# User specified environments
ENVIRONMENTS = [
    "spread", 
    "adversary", 
    "tag"
]

NUM_EPISODES = 10
FIXED_SEED_START = 1
BASE_OUT_DIR = "results/evaluation_table"

def main():
    os.makedirs(BASE_OUT_DIR, exist_ok=True)
    
    # We will build a list of dictionaries, perfect for converting to a table or dataframe
    summary_data = []
    
    start_time = time.time()
    
    for model in MODELS:
        print(f"\n{'='*60}")
        print(f"🚀 STARTING EVALUATION FOR MODEL: {model}")
        print(f"{'='*60}\n")
        
        # Save videos and logs inside model-specific folders
        model_out_dir = os.path.join(BASE_OUT_DIR, model)
        os.makedirs(model_out_dir, exist_ok=True)
        
        for env in ENVIRONMENTS:
            print(f"\n--- Running Env: {env} | Model: {model} | Episodes: {NUM_EPISODES} | Seed: {FIXED_SEED_START} ---")
            
            try:
                # Run the benchmark
                # We use provider='zaiwen' so the API proxy in utils_api handles the model substitution
                result = run_benchmark(
                    env_name=env,
                    provider="zaiwen",
                    episodes=NUM_EPISODES,
                    output_dir=model_out_dir,
                    seed_start=FIXED_SEED_START,
                    model_name=model  # Passed as kwarg to get_api_engine
                )
                
                # Append structured data
                summary_data.append({
                    "Model": model,
                    "Environment": env,
                    "Episodes": NUM_EPISODES,
                    "Mean Reward": round(result.get("mean_reward", 0.0), 4),
                    "Standard Deviation": round(result.get("std_reward", 0.0), 4),
                    "Video Log Dir": model_out_dir,
                    "Status": "Success"
                })
            except Exception as e:
                print(f"❌ Error running {env} with {model}: {str(e)}")
                summary_data.append({
                    "Model": model,
                    "Environment": env,
                    "Episodes": NUM_EPISODES,
                    "Mean Reward": None,
                    "Standard Deviation": None,
                    "Video Log Dir": model_out_dir,
                    "Status": f"Error: {str(e)}"
                })
                
            # Keep updating summary continuously so nothing is lost if it crashes
            summary_path = os.path.join(BASE_OUT_DIR, "summary_table.json")
            with open(summary_path, "w", encoding="utf-8") as f:
                json.dump(summary_data, f, indent=4, ensure_ascii=False)
                
    end_time = time.time()
    print("\n" + "="*60)
    print(f"✅ ALL EVALUATIONS COMPLETED in {end_time - start_time:.2f} seconds!")
    print(f"Summary saved to: {summary_path}")
    print("This JSON format allows easy conversion to Excel, CSV, or markdown tables.")
    print("="*60)

if __name__ == "__main__":
    main()
