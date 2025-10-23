# Personal Finance Tracker

**IST 303 – Fall 2025**  
**Team Paldea: Samantha Aguirre, Gerves Francois Baniakina, Qiao Huang, Rachan Sailamai, Manish Shrivastav**

---

## 📌 Project Overview

This is a Flask-based web application that provides comprehensive personal finance management with focus on budget tracking and expense visualization. The application fulfills Tasks 8 and 9 of the IST 303 course requirements, and serves as a foundation for Milestone 2.0 development.

### ✅ Completed Features (Milestone 1.0)
- **Task 8**: Monthly Budget Setting Interface
- **Task 9**: Budget Progress Visualization with Color-Coded Progress Bars
- User authentication system
- Transaction management (income and expenses)
- Category-based expense tracking
- Financial dashboards and visualizations
- Database setup with SQLite
- Responsive UI with Bootstrap 5
- Testing framework with pytest

---

## 🚀 Key Features

### 📊 Budget Management (Task 8)
- Set monthly spending limits for different categories
- Category-based organization (Groceries, Entertainment, Rent, etc.)
- Form validation and data persistence
- Simple dropdown interface for category selection

### 📈 Progress Visualization (Task 9)
- Real-time budget tracking with visual progress bars
- Color-coded indicators:
  - **Green** = under 70% of budget
  - **Yellow** = 70-90% of budget  
  - **Red** = over 90% of budget
- Spending percentage and remaining amount display
- Budget alerts and warnings

### 💾 Data Management
- SQLite database for local data storage
- Transaction categorization and tracking
- Sample data generator for demonstration
- User-specific budget and transaction storage

---

## 🧱 Tech Stack
- **Python 3.8+**
- **Flask 2.3.2** (Web framework)
- **SQLite** (Local database)
- **Bootstrap 5** (Responsive UI)
- **pytest** (Testing framework)

---

## 📁 Project Structure

```
ist-303-paldea/
│
├── my_paldea/                    # Main application package
│   ├── __init__.py               # Application factory and configuration
│   ├── models.py                 # SQLAlchemy database models
│   ├── views.py                  # Flask view functions and routes
│   ├── config.py                 # Application configuration
│   ├── finSystem.py              # Financial system logic
│   ├── paldea_app/               # Blueprint package
│   │   ├── __init__.py           # Blueprint initialization
│   │   └── views.py              # Blueprint views
│   ├── templates/                # Jinja2 templates
│   │   ├── base.html             # Base template with navigation
│   │   ├── index.html            # Home page
│   │   ├── budget.html           # Budget setting form (Task 8)
│   │   ├── budget_progress.html  # Progress visualization (Task 9)
│   │   ├── login.html            # User authentication
│   │   ├── register.html         # User registration
│   │   ├── home.html             # User dashboard
│   │   ├── edit_transaction.html # Transaction editing
│   │   ├── part_c.html           # Milestone presentation
│   │   └── demo.html             # Demo page
│   └── static/                   # Static assets
│       ├── css/main.css          # Custom styling
│       ├── js/main.js            # JavaScript functionality
│       └── burndown_chart.jpg    # Burndown chart image
│
├── scripts/                      # Utility scripts
│   └── init_db.py                # Database initialization
├── visuals/                      # Visual assets
│   └── Burn Chart as on Oct 23 1.jpg # Burndown chart source
├── app.py                        # Main Flask application entry point
├── run.py                        # Development server runner
├── requirements.txt              # Python dependencies
├── setup.py                      # Package setup configuration
├── TODO.md                       # Project task tracking
├── TASKS_8_9_DOCUMENTATION.md    # Task documentation
├── TASKS_8_9_PLAN.md             # Task planning
├── MERGE_SUMMARY.md              # Merge documentation
├── MILESTONE_2_PLAN.md           # Milestone 2.0 planning
├── README.md                     # This file
├── my_paldea/app.db              # SQLite database
└── .git/                         # Git repository
```

---

## 🛠 Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

If you don't have Python installed, install it from https://www.python.org/.

### Quick install (macOS)

Clone the repository, create a virtual environment, install dependencies, and start the app:

```bash
git clone https://github.com/rscgu/ist-303-paldea.git
cd ist-303-paldea
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python run.py
```

After the server starts, open <http://127.0.0.1:5000> in your browser.

If you prefer Windows, use `python -m venv venv` and `venv\Scripts\activate` to activate the venv.

### Configuration

- The app uses a local SQLite database by default (`my_paldea/app.db`).
- Use `scripts/init_db.py` to initialize or reset sample data (read the script before running).

---

## ▶️ Running and usage

The application provides user registration/login and a dashboard for transactions and budgets. Key routes (when running locally):

- Home: <http://127.0.0.1:5000/>
- Login: <http://127.0.0.1:5000/login>
- Register: <http://127.0.0.1:5000/register>
- Dashboard/Home (after login): <http://127.0.0.1:5000/home>
- Set Budget: <http://127.0.0.1:5000/budget>
- View Progress: <http://127.0.0.1:5000/budget_progress>

Usage notes:

- Create an account, then add transactions (income/expense) from the dashboard.
- Set monthly budgets by category on the "Set Budget" page.
- View color-coded progress bars on the budget progress page (green/yellow/red thresholds are roughly 70% and 90%).

---

## � Testing

Run the project's tests with pytest. From the project root (venv activated):

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=my_paldea

# Generate HTML coverage report
pytest --cov=my_paldea --cov-report=html
```

Known test coverage: ~87% (project-reported). Add or update tests in `tests/` if present.

---

## 📦 Project structure (summary)

High-level layout (see repository for full details):

```
my_paldea/        # application package (models, views, templates, static)
scripts/          # utility scripts (init_db.py)
app.py, run.py    # app entry points
requirements.txt  # Python deps
README.md          # this file
```

---

## 🤝 Contributing

Contributions are welcome. Small, focused pull requests work best.

Suggested workflow:

1. Fork the repository and create a feature branch.
2. Add tests for new behavior where appropriate.
3. Ensure the test suite passes locally.
4. Create a PR describing the change and linking any relevant issue.

Coding style:

- Prefer small, well-scoped commits.
- Follow existing code conventions (PEP8 for Python).

---

## 📧 Contacts & acknowledgements

Team Paldea — IST 303, Fall 2025

- Samantha Aguirre — samantha.aguirre@cgu.edu
- Gerves Francois Baniakina — gerves.baniakina@cgu.edu
- Qiao Huang — qiao.huang@cgu.edu
- Rachan Sailamai — rachan.sailamai@cgu.edu
- Manish Shrivastav — manish.shrivastav@cgu.edu

Please open issues in the repository for bugs or feature requests.

---

_Last updated: October 23, 2025_
