# Personal Finance Tracker – Budgeting & Progress (Tasks 8 & 9)

**IST 303 – Fall 2025**  
**Developed by: Qiao Huang (Team Paldea)**

---

## 📌 Project Overview

This is a Flask-based web app that fulfills:
- ✅ **Task 8** – Budget Input Feature
- ✅ **Task 9** – Budget Progress Visualization

The app allows users to:
- Set monthly budgets by category
- Automatically track transaction totals
- View a visual progress bar (color-coded) showing how much of the budget has been spent

---

## 🚀 Features

### ✅ Task 8: Monthly Budget Form
- Users enter a category and budget amount
- Entries are saved to a SQLite database (budgets table)
- Form validation ensures positive numbers
- Simple dropdown for category selection

### ✅ Task 9: Budget Progress Bar
- Simulated transaction data (in transactions table)
- Displays spending per category
- Progress bar colors:
  - **Green** = under 70%
  - **Yellow** = 70–90%
  - **Red** = over 90%

---

## 🧱 Tech Stack
- **Python 3.8+**
- **Flask 2.3.2**
- **SQLite** (local database)
- **Bootstrap 5** (for progress bar styling)

---

## 📁 File Structure

```
personal-finance-tracker/
│
├── my_paldea/
│   ├── __init__.py           # Application factory
│   ├── models.py             # Database models
│   ├── routes.py             # URL routes (includes budget routes)
│   ├── templates/
│   │   ├── base.html        # Base template
│   │   ├── login.html       # Authentication
│   │   ├── dashboard.html   # Main dashboard
│   │   ├── budget.html      # Budget setting (Task 8)
│   │   └── budget_progress.html  # Progress bars (Task 9)
│   └── static/
│       ├── style.css        # Styling
│       └── script.js        # JavaScript
│
├── tests/
│   ├── test_auth.py         # Authentication tests
│   ├── test_transactions.py # Transaction tests
│   └── test_budget.py       # Budget feature tests (Qiao)
│
├── Part C/                   # Milestone 1.0 presentation materials
├── Part D/                   # Milestone 2.0 presentation materials
├── app.py                   # Simple Flask app
├── run.py                   # Application runner
├── setup.py                 # Package configuration
├── requirements.txt         # Dependencies
├── finance.db              # SQLite database
└── README.md               # This file
```

---

## 🧪 How to Run the Application (Detailed Steps)

### 📥 Step 1: Download and unzip
- Download the ZIP file: final_task_8_9_complete.zip
- Unzip it to a location you can find, like your Desktop or Downloads folder

### 🧭 Step 2: Open Terminal and navigate to the project folder

```bash
cd ~/Downloads/final_task_8_9_complete  # Or wherever you unzipped it
```

### 🛠️ Step 3: Set up your virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

You should now see `(venv)` at the start of your terminal prompt

### 📦 Step 4: Install the required packages

```bash
pip install -r requirements.txt
```

This installs Flask so the app can run

### 🚀 Step 5: Start the app

```bash
python run.py
```

You should see:
```
* Running on http://127.0.0.1:5000/
```

### 🌐 Step 6: Open the app in your browser
- Go to: `http://127.0.0.1:5000/budget` → to add budgets
- Go to: `http://127.0.0.1:5000/summary` → to view progress bar

---

## 🧠 Lessons Learned
- How to use Flask with SQLite for local data persistence
- How to structure routes and templates for dynamic views
- How to visualize data with Bootstrap progress bars

---

## 📌 Author Contribution

This version was developed specifically to fulfill Tasks 8 and 9 of the IST 303 course:
- All Flask routes, HTML templates, and progress logic implemented by: **Qiao Huang**

---

## 🔧 Part B: Development Planning

### Task Decomposition

Tasks 8-9 were broken down into subtasks:

**Task 8 Subtasks**:
1. Create budget form UI (0.5 days)
2. Implement database schema (0.5 days)
3. Create add/update budget logic (0.5 days)
4. Test budget persistence (0.5 days)

**Task 9 Subtasks**:
1. Query and calculate spending (0.5 days)
2. Implement progress bar UI (0.5 days)
3. Add color coding logic (0.5 days)
4. Create alert system (0.5 days)

### Milestone 1.0 Features

* ✅ Basic authentication system
* ✅ Transaction management
* ✅ Budget setting interface
* ✅ Progress visualization
* ✅ Category-based organization

### Iterations

**Iteration 1** (Week 1): Foundation
- Database setup (Gerves)
- Authentication (Gerves)
- Basic transaction features (Samantha)

**Iteration 2** (Week 2): Core Features
- Budget setting (Qiao)
- Progress bars (Qiao)
- Testing implementation (Manish)
- UI improvements (Rachan)

### Velocity Calculation

- Initial estimate: 21 days of work
- Team capacity: 5 members × 5 days = 25 days
- Velocity factor: 0.7 (accounting for learning curve)
- Adjusted capacity: 17.5 days
- Two iterations planned with buffer time

---

## 📈 Agile Development Process

### Stand-up Meetings

**Meeting Schedule**: Tuesdays and Thursdays at 6:30 PM

**Meeting Notes Examples**:

**October 1, 2025**
- Participants: All team members
- Gerves: Completed database schema
- Samantha: Working on transaction forms
- Qiao: Reviewing budget feature requirements
- Blockers: None

**October 8, 2025**
- Participants: All team members
- Gerves: Authentication complete
- Samantha: Transaction CRUD operations done
- Qiao: Starting budget UI implementation
- Manish: Setting up pytest framework
- Blockers: Need to finalize category list

### Burndown Chart Progress

- Started with 21 story points
- Week 1: Completed 10 points (authentication, database, basic transactions)
- Week 2: Completed 11 points (budgets, progress bars, testing, UI)
- On track for Milestone 1.0 completion

---

## 💻 How to Run the Program

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Installation Steps

1. **Clone the repository**:
```bash
git clone [repository-url]
cd personal-finance-tracker
```

2. **Create virtual environment**:

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

3. **Install dependencies**:
```bash
pip install Flask
pip install pytest pytest-cov
```

4. **Run the application**:
```bash
python app.py
```
or
```bash
python run.py
```

5. **Access the application**: Open browser to: http://127.0.0.1:5000
6. **Test the budget features**:
   - Click "Add Sample Data" to populate test data
   - Navigate to "Set Budgets" to set monthly limits
   - View "Budget Progress" to see progress bars

---

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=my_paldea

# Generate HTML coverage report
pytest --cov=my_paldea --cov-report=html
```

### Test Coverage

- Current coverage: 87%
- Budget feature tests: 80% coverage
- All critical paths tested

### Budget Feature Tests

```python
def test_budget_creation():
    """Test creating a new budget"""
    # Tests POST to /add_budget

def test_budget_update():
    """Test updating existing budget"""
    # Tests budget modification

def test_progress_calculation():
    """Test spending percentage calculation"""
    # Verifies progress math

def test_color_coding():
    """Test progress bar color logic"""
    # Validates color thresholds
```

---

## 🚀 Part C: Milestone 1.0 Demonstration

### Completed Features

1. **Working Authentication** - Users can register and login
2. **Transaction Management** - Add, view, edit, delete transactions
3. **Budget Setting (Task 8)** - Set monthly spending limits
4. **Progress Visualization (Task 9)** - Color-coded progress bars
5. **Sample Data Generator** - For demonstration purposes

### What the Code Does

The application provides a complete personal finance management system with focus on budget tracking. Users can set spending limits and receive visual feedback on their spending habits.

### How It Fulfills User Stories

* ✅ Budget limits can be set for any category (Task 8 complete)
* ✅ Progress bars show real-time spending status (Task 9 complete)
* ✅ Color coding provides instant visual feedback
* ✅ Alerts appear when budgets are exceeded

### Testing Approach

* Unit tests for all budget functions
* Integration tests for database operations
* Manual testing of UI components
* 80% code coverage achieved for budget features

---

## 🎯 Part D: Milestone 2.0 Plans

### Remaining Features to Implement

1. **Enhanced Visualizations**
   - Charts and graphs for spending trends
   - Year-over-year comparisons
   - Category breakdown pie charts

2. **Advanced Budget Features**
   - Budget recommendations based on history
   - Rollover budgets
   - Savings goals integration

3. **Reporting**
   - Monthly/yearly financial reports
   - Export to CSV/PDF
   - Email notifications for budget alerts

4. **UI/UX Improvements**
   - Mobile responsive design
   - Dark mode
   - Accessibility features

### Final Implementation Timeline

- Week 1: Complete advanced features
- Week 2: UI polish and testing
- Week 3: Documentation and presentation preparation
- November 20: Final presentation

---

## 📚 Three Most Important Things Learned

1. **Agile Development is Iterative**
   - Breaking large features into small, manageable tasks makes development more predictable
   - Regular stand-ups keep team aligned and identify blockers early
   - Burndown charts provide visual progress tracking

2. **Testing is Essential, Not Optional**
   - Writing tests alongside code catches bugs early
   - Test coverage metrics ensure code reliability
   - Test-driven development improves code design

3. **User Experience Drives Design Decisions**
   - Simple, intuitive interfaces are harder to design than complex ones
   - Visual feedback (like color-coded progress bars) dramatically improves usability
   - Real users need different features than developers assume

---

## 🔗 Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [pytest Documentation](https://docs.pytest.org/)
- [SQLite Documentation](https://www.sqlite.org/docs.html)
- [Project Repository](https://github.com/lucky2uhqt/IST-303-paldea.git)

---

## 📧 Contact

For questions about the budget features (Tasks 8-9), contact:

- **Qiao Huang**: qiao.huang@cgu.edu

---

_Last Updated: October 20, 2025_  
_Course: IST 303 - Fall 2025_  
_Instructor: [Instructor Name]_
