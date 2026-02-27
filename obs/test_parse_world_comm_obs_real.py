import numpy as np
from pettingzoo.mpe import simple_world_comm_v3
from obs.parse_world_comm_obs import parse_world_comm_obs

if __name__ == "__main__":
    env = simple_world_comm_v3.parallel_env()
    obs, _ = env.reset()
    for k, v in obs.items():
        print(f"\nAgent: {k}")
        print("Raw obs:", v.tolist())
        parsed = parse_world_comm_obs(v, k)
        print("Parsed:", parsed)
