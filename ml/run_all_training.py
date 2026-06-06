import os
import subprocess
from pathlib import Path

def load_env():
    env_path = Path(".env")
    if env_path.exists():
        with open(env_path, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    key, val = line.split("=", 1)
                    os.environ[key.strip()] = val.strip()

def run_train(target):
    print(f"========== Training {target} ==========")
    # Run the training script via subprocess so it inherits the env vars
    cmd = ["python", "src/models/train.py", "--target", target]
    subprocess.run(cmd, env=os.environ, check=True)

if __name__ == "__main__":
    load_env()
    
    if "HF_TOKEN" not in os.environ:
        print("WARNING: HF_TOKEN not found in .env!")
    
    targets = ["Position"]
    for t in targets:
        run_train(t)
    
    print("All models trained and deployed successfully!")
