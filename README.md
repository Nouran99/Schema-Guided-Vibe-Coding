# 1. Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env and add your DEEPSEEK_API_KEY

# 4. Validate installation
python test_imports.py

# 5. Run experiment
python run_experiment.py

## Output Structure

After running, you'll get this structure:

```
output/
└── build_a_simple_calculator_20260111_143022/
    ├── README.md                    # Project documentation
    ├── experiment_results.json      # Full experiment data
    ├── run_backend.bat              # Windows run script
    ├── run_backend.sh               # Linux/Mac run script
    │
    ├── backend/                     # Executable backend code
    │   ├── main.py                  # FastAPI application
    │   └── models.py                # Pydantic models
    │
    ├── frontend/                    # Executable frontend code
    │   └── index.html               # HTML with embedded CSS/JS
    │
    └── phases/                      # Raw agent outputs
        ├── 01_user_stories.json
        ├── 02_system_design.json
        ├── 03_backend_code.json
        ├── 04_frontend_code.json
        └── 05_test_report.json
```

---

## How to Run

### Option 1: Quick Test
```bash
python run_experiment.py "Build a simple calculator"
```

### Option 2: Interactive Menu
```bash
python run_experiment.py
```

### Option 3: Direct Python
```python
from src.crew import PentagonCrew

crew = PentagonCrew(verbose=True, output_dir="output")
result = crew.run("Build a todo list app")

print(f"Output saved to: {result['output_directory']}")
```

---

## Running the Generated Code

After generation:

```bash
# 1. Go to output directory
cd output/build_a_simple_calculator_20260111_143022

# 2. Run backend
cd backend
pip install fastapi uvicorn pydantic
uvicorn main:app --reload --port 8000

# 3. In another terminal, serve frontend
cd ../frontend
python -m http.server 3000

# 4. Open browser to http://localhost:3000
```

Or on Windows, just double-click `run_backend.bat`
