import os
import glob
import joblib
import catboost as cb
from huggingface_hub import HfApi
from pathlib import Path
import sys

# We deleted wrappers.py, so joblib.load will fail looking for it.
# Let's create a mock module and class and inject it into sys.modules so joblib can unpickle it.
import types

mock_module = types.ModuleType("src.models.wrappers")
class AutoCatBoostRegressor(cb.CatBoostRegressor):
    pass
mock_module.AutoCatBoostRegressor = AutoCatBoostRegressor
sys.modules["src"] = types.ModuleType("src")
sys.modules["src.models"] = types.ModuleType("src.models")
sys.modules["src.models.wrappers"] = mock_module

def migrate_model(model):
    migrated = False

    if hasattr(model, 'estimators'):
        for i, (name, est) in enumerate(model.estimators):
            if type(est).__name__ == 'AutoCatBoostRegressor':
                est.__class__ = cb.CatBoostRegressor
                migrated = True
                print(f"  - Migrated unfitted estimator: {name}")

    if hasattr(model, 'named_estimators_'):
        for name, est in model.named_estimators_.items():
            if type(est).__name__ == 'AutoCatBoostRegressor':
                est.__class__ = cb.CatBoostRegressor
                migrated = True
                print(f"  - Migrated named_estimator: {name}")

    if hasattr(model, 'estimators_'):
        for est in model.estimators_:
            if type(est).__name__ == 'AutoCatBoostRegressor':
                est.__class__ = cb.CatBoostRegressor
                migrated = True
                print(f"  - Migrated fitted estimator_")

    return migrated

def main():
    project_root = Path(__file__).resolve().parent
    model_paths = []
    
    backend_pattern = project_root / 'backend' / 'models' / '*' / '*' / 'model.pkl'
    model_paths.extend(glob.glob(str(backend_pattern)))
    
    ml_pattern = project_root / 'ml' / 'artifacts' / '*' / '*' / 'model.pkl'
    model_paths.extend(glob.glob(str(ml_pattern)))
    
    model_paths = list(set(model_paths))
    
    print(f"Found {len(model_paths)} models to inspect.")
    
    hf_token = os.environ.get("HF_TOKEN")
    hf_repo_id = os.environ.get("HF_REPO_ID", "Maheeth1/f1-race-predictor")
    api = HfApi() if hf_token else None

    for path in model_paths:
        path = Path(path)
        print(f"\nInspecting {path}...")
        try:
            model = joblib.load(path)
            
            if migrate_model(model):
                print(f"  Saving migrated model to {path}")
                joblib.dump(model, path)
                
                if api:
                    parts = path.parts
                    target = parts[-3]
                    version = parts[-2]
                    filename = parts[-1]
                    
                    repo_path = f"{target}/{version}/{filename}"
                    print(f"  Uploading to Hugging Face: {repo_path}")
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
            else:
                print("  No migration needed.")
        except Exception as e:
            print(f"  Failed to process {path}: {e}")

if __name__ == '__main__':
    main()
