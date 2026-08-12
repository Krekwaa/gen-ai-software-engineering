# How to Run Homework 2

From `homework-2`:

```powershell
python -m pip install -r requirements.txt
python -m pytest
python -m uvicorn src.backend.app.main:app --reload
```

In a second terminal, serve the frontend:

```powershell
python -m http.server 5173 -d src/frontend
```

Open `http://127.0.0.1:5173`. API documentation is available at `http://127.0.0.1:8000/docs`.

