# Personal Finance Tracker

**IST 303 – Fall 2025**  
**Team Paldea: Samantha Aguirre, Gerves Francois Baniakina, Qiao Huang, Rachan Sailamai, Manish Shrivastav**

---

## 📌 Project Overview

This is a Flask-based web application that provides comprehensive personal finance management with focus on budget tracking and expense visualization. The application fulfills Tasks 8 and 9 of the IST 303 course requirements, and serves as a foundation for Milestone 2.0 development.

[PowerPoint Presentation for Milestone 1.0](https://cgu0-my.sharepoint.com/:p:/g/personal/qiao_huang_cgu_edu/EdifK9rv8HxDlJWIs-DtM78B1VZF1vDlgoMh6u3Lb9zbBA)

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


[PowerPoint Presentation for Milestone 2.0](https://cgu0-my.sharepoint.com/:p:/g/personal/samantha_aguirre_cgu_edu/IQCZYCKRrxvxRIeDlsjw0FK5AbSWBvS_q7hflXWORSc6sUA?e=snV4mZ)
### ✅ Completed Features (Milestone 2.0)
- **Phase 1**: Data Export & Reporting (Tasks 25-28)
  - CSV export functionality
  - PDF financial reports with charts
  - Tax preparation summaries
  - Scheduled report generation
- **Phase 2**: Enhanced Visualization (Tasks 21-24)
  - Trend line charts for spending patterns
  - Forecasting algorithms
  - Interactive drill-down charts
  - Custom dashboard layouts
- **Phase 3**: Multi-Currency Support (Tasks 45-48)
  - Currency exchange rate API integration
  - Multi-currency transaction handling
  - Currency preference settings
  - Currency conversion history tracking

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
│       ├── burndown_chart.jpg    # Burndown chart image
|       └── Burndown chart 11-20-15 # Burndown chart image final
│
├── scripts/                      # Utility scripts
│   └── init_db.py                # Database initialization
├── visuals/                      # Visual assets
│   ├── Burndown chart 11-20-15   # Burndown chart image source
|   └── Burn Chart as on Oct 23   # Burndown chart source
├── my_paldea_part_d/             # Additional views for Part D
│   └── secondary_views.py        # Secondary view functions
├── tests/
│   ├── conftest.py               #Provides client and logged_in_client fixtures
│   ├── test_auth.py              #Login success, login failure, and access protection for /home
│   ├── test_home.py              #That the /home dashboard loads correctly for a logged-in user
│   ├── test_transactions.py      #Adding a new transaction via the /add_transaction route
│   ├── test_budgets.py           #Submitting a category budget through /set_category_budget
│   └── test_exports.py           #CSV export (/financial_report_csv) and PDF export (/financial_report_pdf
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

##  Testing

Testing

This project includes an automated test suite built using pytest and pytest-cov.
To run the tests, first activate your virtual environment and navigate to the project root directory.
Run all tests
pytest

Run tests with coverage reporting
pytest --cov=my_paldea --cov-report=term-missing

Generate an HTML coverage report
pytest --cov=my_paldea --cov-report=html


An htmlcov/ folder will be created. Open the report in a browser:

htmlcov/index.html

Current Test Coverage (Milestone 2.0)

| Module / Component                 | Coverage |
| ---------------------------------- | -------- |
| Configuration (`config.py`)        | 100%     |
| Database Models (`models.py`)      | 92%      |
| App Initialization (`__init__.py`) | 83%      |
| Utility Functions                  | 70%      |
| Application Views (`views.py`)     | 48%      |
| Financial Logic (`finSystem.py`)   | 9%       |
| **Overall Coverage**               | **55%**  |

Test Summary

Total tests: 8

All tests passed successfully

Covers:

Authentication

Access control

Dashboard rendering

Transaction creation

Budget creation

CSV & PDF export

During testing, we discovered that the original PDF export route depended on an external headless browser (Chrome/Edge). As a result, the route behaved inconsistently across machines — returning 200 OK only when a headless browser was available, and 500 Server Error when it was not. This affected our automated tests, which initially needed to accept either status code.

---

## 📦 Project structure (summary)

High-level layout (see repository for full details):

```
my_paldea/        # application package (models, views, templates, static)
scripts/          # utility scripts (init_db.py)
app.py, run.py    # app entry points
requirements.txt  # Python deps
tests/test_auth.py
tests/test_home.py
tests/test_transactions.py
tests/test_budgets.py
tests/test_exports.py
README.md          # this file
```

---
## Key Learnings from This Project

1. Agile/Scrum improves teamwork and delivery consistency — Working in structured sprints, maintaining a burndown chart, and tracking velocity taught us how to plan realistically, adapt quickly, and stay aligned as a team.

2. Automated testing is essential for stable software — Building pytest tests and tracking coverage helped us catch issues early, verify behavior after changes, and gain confidence that core features (login, budgets, transactions, exports) were working correctly.

3. Clean architecture makes collaboration easier — Separating logic into models, routes, templates, and utilities made the code more maintainable, reduced merge conflicts, and allowed team members to develop features in parallel without blocking each other.


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
- Manish Shrivastav — manish.ranjan.shrivastav@cgu.edu

Please open issues in the repository for bugs or feature requests.

---

_Last updated: November 20, 2025_
