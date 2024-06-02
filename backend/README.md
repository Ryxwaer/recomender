## Run FastAPI app locally
- using venv and uvicorn
```bash
pip -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

## To improve

- Use database instead of local CSV files
- Optimize recommender algorithm
- Preload top books for faster response
- add proper logging