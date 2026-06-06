import os
import glob
from huggingface_hub import HfApi
from pathlib import Path

def main():
    project_root = Path(__file__).resolve().parent
    model_paths = []
    
    backend_pattern = project_root / 'backend' / 'models' / '*' / '*' / 'model.pkl'
    model_paths.extend(glob.glob(str(backend_pattern)))
    
    ml_pattern = project_root / 'ml' / 'artifacts' / '*' / '*' / 'model.pkl'
    model_paths.extend(glob.glob(str(ml_pattern)))
    
    model_paths = list(set(model_paths))
    
    hf_token = os.environ.get("HF_TOKEN")
    if not hf_token:
        try:
            with open(project_root / 'ml' / '.env', 'r') as f:
                for line in f:
                    if line.startswith('HF_TOKEN='):
                        hf_token = line.strip().split('=', 1)[1]
                        break
        except Exception:
            pass
            
    hf_repo_id = os.environ.get("HF_REPO_ID", "Maheeth1/f1-race-predictor")
    api = HfApi() if hf_token else None

    if not api:
        print("HF_TOKEN not found in environment!")
        return

    for path in model_paths:
        path = Path(path)
        parts = path.parts
        target = parts[-3]
        version = parts[-2]
        filename = parts[-1]
        
        repo_path = f"{target}/{version}/{filename}"
        print(f"Uploading {path} to Hugging Face: {repo_path}")
        try:
            api.upload_file(
                path_or_fileobj=str(path),
                path_in_repo=repo_path,
                repo_id=hf_repo_id,
                token=hf_token,
                commit_message=f"Migrate custom wrappers to native classes for {target} {version}"
            )
            print("  Upload successful!")
        except Exception as e:
            print(f"  Upload failed: {e}")

if __name__ == '__main__':
    main()
