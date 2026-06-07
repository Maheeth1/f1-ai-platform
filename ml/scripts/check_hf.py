from huggingface_hub import HfApi

api = HfApi()
try:
    files = api.list_repo_tree(repo_id="Maheeth1/f1-race-predictor", repo_type="model")
    for f in files:
        print(f.path)
except Exception as e:
    print(f"Error: {e}")
