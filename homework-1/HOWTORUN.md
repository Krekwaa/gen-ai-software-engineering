# How to Run Homework 1

From `homework-1`:

```powershell
python -m pip install -r requirements.txt
python -m pytest -q
python -m uvicorn src.app:app --reload
```

Open `http://127.0.0.1:8000/docs` for interactive Swagger documentation or run the requests in `demo/sample-requests.http`.

