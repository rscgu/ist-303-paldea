# Personal Finance Tracker

**IST 303 – Fall 2025**  
**Team Paldea: Samantha Aguirre, Gerves Francois Baniakina, Qiao Huang, Rachan Sailamai, Manish Shrivastav**

---

## 📌 Project Overview

This is a Flask-based web application that provides comprehensive personal finance management with focus on budget tracking and expense visualization. The application fulfills Tasks 8 and 9 of the IST 303 course requirements.

### ✅ Completed Features
- **Task 8**: Monthly Budget Setting Interface
- **Task 9**: Budget Progress Visualization with Color-Coded Progress Bars
- User authentication system
- Transaction management (income and expenses)
- Category-based expense tracking
- Financial dashboards and visualizations

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
personal-finance-tracker/
│
├── my_paldea/
│   ├── __init__.py           # Application factory
│   ├── models.py             # Database models
│   ├── views.py              # View functions
│   ├── config.py             # Configuration
│   ├── finSystem.py          # Financial system logic
│   ├── templates/
│   │   ├── base.html         # Base template
│   │   ├── index.html        # Home page
│   │   ├── budget.html       # Budget setting form
│   │   ├── budget_progress.html # Progress visualization
│   │   ├── login.html        # Authentication
│   │   └── register.html     # User registration
│   └── static/
│       ├── css/main.css      # Custom styling
│       └── js/main.js        # JavaScript functionality
│
├── Part C/                   # Milestone 1.0 presentation materials
├── app.py                    # Main Flask application
├── budget_routes.py          # Budget-specific routes
├── run.py                    # Application runner
├── requirements.txt          # Python dependencies
├── finance.db               # SQLite database
└── README.md                # This file
```

---

## 🛠️ Installation and Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Installation Steps

1. **Clone the repository**:
   ```bash
   git clone https://github.com/lucky2uhqt/IST-303-paldea.git
   cd ist-303-paldea
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
   pip install -r requirements.txt
   ```

4. **Run the application**:
   ```bash
   python app.py
   ```
   or
   ```bash
   python run.py
   ```

5. **Access the application**: Open browser to `http://127.0.0.1:5000`

---

## 🧪 How to Use the Application

### Getting Started
1. **Set your budgets**: Navigate to "Set Budget" to define spending limits for different categories
2. **Add sample data**: Click "Add Sample Data" to populate the system with example transactions
3. **View progress**: Click "View Progress" to see visual progress bars for each budget category
4. **Track spending**: Monitor your progress throughout the month to stay within budget

### Key URLs
- **Home**: `http://127.0.0.1:5000/`
- **Set Budget**: `http://127.0.0.1:5000/budget`
- **View Progress**: `http://127.0.0.1:5000/budget_progress`
- **Add Sample Data**: `http://127.0.0.1:5000/add_sample_data`

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

---

## 📈 Agile Development Process

### Team Structure
- **Samantha Aguirre**: Transaction management and UI
- **Gerves Francois Baniakina**: Database setup and authentication
- **Qiao Huang**: Budget features (Tasks 8 & 9)
- **Rachan Sailamai**: UI/UX improvements
- **Manish Shrivastav**: Testing and quality assurance

### Development Timeline
- **Week 1**: Foundation (Database, Authentication, Basic Transactions)
- **Week 2**: Core Features (Budget Setting, Progress Bars, Testing, UI)
- **Week 3**: Polish and Documentation

### Stand-up Meetings
- **Schedule**: Tuesdays and Thursdays at 6:30 PM
- **Focus**: Progress updates, blocker identification, task coordination

---

## 🎯 Milestone Achievements

### ✅ Milestone 1.0 (Completed)
- Working authentication system
- Transaction management (CRUD operations)
- Budget setting interface (Task 8)
- Progress visualization with color-coded bars (Task 9)
- Sample data generator for demonstration

### 🚀 Milestone 2.0 (Planned)
- Enhanced visualizations (charts and graphs)
- Advanced budget features (rollover budgets, recommendations)
- Reporting system (monthly/yearly reports)
- Mobile responsive design improvements

---

## 📚 Key Learnings

1. **Agile Development is Iterative**
   - Breaking large features into manageable tasks improves predictability
   - Regular stand-ups keep teams aligned and identify blockers early
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
- [Bootstrap 5 Documentation](https://getbootstrap.com/docs/5.1/)
- [Project Repository](https://github.com/lucky2uhqt/IST-303-paldea.git)

---

## 📧 Contact

For questions about the project, contact the development team:

- **Samantha Aguirre**: samantha.aguirre@cgu.edu
- **Gerves Francois Baniakina**: gerves.baniakina@cgu.edu  
- **Qiao Huang**: qiao.huang@cgu.edu
- **Rachan Sailamai**: rachan.sailamai@cgu.edu
- **Manish Shrivastav**: manish.shrivastav@cgu.edu

---

_Last Updated: October 20, 2025_  
_Course: IST 303 - Fall 2025_  
_Instructor: [Instructor Name]_

Date:September 24, 2025 at 6:30PM
Participannts: Samantha Aguirre, Manish Ranjan Shrivastav, Gerves Francois Baniakina
Focused on clarifying Milestone One requirements and logistics.


Personal Finance Tracker 
Team members: Samantha Aguirre, Gerves Francois Baniakina, Qiao Huang, Rachan Sailamai, Manish
Shrivastav
1. Met 
2. Concept 
The personal finance tracker is an application that allows users to record daily financial transactions, 
categorize expenses, and visualize spending patterns. It provides a simple, user-friendly interface 
connected to an underlying database, enabling structured storage and retrieval of financial data. The app 
bridges the gap between raw data (transactions in a database) and meaningful insights (charts, 
summaries, budgets), making it easy for users to understand and control their finances. 
3. Stakeholders 
* End Users: 
	* People who want to track daily expenses and income
 	* Students, Professionals, families managing budgets o Privacyconscious users who dislike cloud-only finance app 
* Developers and Contributors 
* UI and UX Designers 
* Data Analysts and Researchers 
* Testers 
4. Initial Set of Project Requirements expressed as user stories with estimates completion times
* As a user of the product, I need a better financial system that wouldn’t require me to sign up for 
multiple software or services. I want this user story to be implemented in two days.
*  As a user of the product, I need a better financial system that performs custom formulas, creates 
beautiful design layouts, synchronizes databases, customizes formulas, and automates 
calculations. This financial system should help me handle everyday financial management 
including calculating a monthly budget and showing available budget for different spending 
categories; tracking expenses, income sources, transfers in one place; tracking upcoming 
subscriptions bill and their due dates; monitoring my investments to track gains and losses; 
monitoring debt balances and payments schedules; accessible financial dashboard that displays 
financial summaries. Each month I can easily reviews my total income, expenses, and cash flow. I 
want this user story to be implemented in 4 days.
* As a user of the product, I need a personal financial tracker that can help me allocate how much I 
want to save, invest, spend, and pay off each month. This user story can be implemented in 4 
days.
* As a user of the product, I want a personal financial system that can display a flag or alert me 
when my budget is exhaustive and prevent me from exceeding the budget. My financial reports 
should display progress bars or indicators to show how well I am doing financially each month. I 
want this user story to be implemented in two days.
* As a user of the product, I want custom filters to help me easily trace back financial progress 
from previous and years.
* As a user of the product, I want an income tracker that can record an income transaction, 
categorize the income sources – whether it’s a freelance work, online business, rental income or 
dividends. I want this user story to be implemented in 3 days.
* As a user of the product, I want an expense tracker that can organize all my expense records by 
category or subcategory so that my personal financial system helps me identify where I can cut 
back and save money. The user story should be done 3 days.
* As a user of the product, I want a receipt tracker that, each time an expense transaction is 
added, I can upload a PDF receipt or link to an external URL containing the file and indicate if it is 
tax deductible. This user story can be implemented in 3 days.
* As a user of the product, I need a component tracker that should keep track of all my personal 
and business subscriptions like Netflix, hosting providers, design software, etc.This tracker should 
automatically count down to the next billing date and indicate the number of days until my 
payment. I want this application to be implemented in 3 days.
* As a user of the product, I need a financial tracker that can pin upcoming reminders on the 
dashboard to highlight payment due within the next coming interval of days. I want the user 
story to be done I 1 day.
* As a user of the product, I need an investment tracker that can help me monitor my investment 
in one place. This system will also allow me to categorize investment assets such as stocks, 
cryptocurrencies, index funds, mutual funds, hedge funds, and real estate. On my request it can 
update the current market value, and it will automatically calculate the percentage of gains and 
losses across all investment assets. I want this user story to be implemented in 4 days.
* As a user of the product, I want a real-time account balance tracker to monitor all my bank 
accounts and track transfer activities between accounts. After each transaction the balances in 
my account manager update automatically in real time so that I always have the most accurate 
and up-to-date information about my assets at the fingertips so that I don’t have to recalculate 
everything. This account balance tracker should also integrate with the net worth calculation 
database such as whenever bank balances change, my personal financial system gallery will 
automatically my total assets, liabilities and net worth. I want this user story to be implemented 
in 4 days.
* As a user of the product, I want a loan tracker to manage my loans. This loan tracker should 
categorize them based on interest rates, allowing me to prioritize and save money on interest 
over time. This loan tracker should have the ability to auto-count down and displays exactly 
when and how much more I need to pay off my debt. This will allow me to watch the days and 
amount decrease in real time as I make payments. This user story must be implemented in 3 
days.
* As a user of the product, I would like to set annual financial targets, such as how much I want to 
earn, to save, invest, and pay off each year. So, I want a tracker that will automatically calculate 
how much I am currently achieving my goals, and progress marker will show how close I am to 
reaching my financial targets. I want this user story to be implemented in 4 days.
* As the user of the product, I want the financial system to include financial literacy prompts,
savings tips

## Epics and Tasks

### Epic 1: Core Transaction Management
(Allocated to Gerves)
Linked User Stories: 1, 6, 7
Summary: These stories describe the need for a unified system where users can record and categorize both income and expense transactions without relying on multiple services.

- Task 1: Set up user authentication (login, register). (Supports Story 1: unified financial system with no extra signups)
- Task 2: Create database schema (users, transactions, categories). (Foundation for Stories 6 & 7)
- Task 3: Implement “Add income transaction” form. (Supports Story 6: income tracker)
- Task 4: Implement “Add expense transaction” form. (Supports Story 7: expense tracker)

### Epic 1.2: Core Transaction Management Continued
(Allocated to Samantha)
Linked User Stories: 1, 6, 7
Summary: These stories describe the need for a unified system where users can record and categorize both income and expense transactions without relying on multiple services.

- Task 5: Categorize transactions by income/expense type. (Supports Stories 6 & 7)
- Task 6: Display transactions in a list view. (Supports Stories 6 & 7)
- Task 7: Implement delete/edit transaction functionality. (Enhances Stories 6 & 7 usability)

### Epic 2: Budgeting & Alerts
(Allocated to Qiao)
Linked User Stories: 3, 4, 14

- Task 8: Monthly Budget Feature
  What it does:
  Allows users to set spending limits for different expense categories
  Users select a category (Groceries, Entertainment, Rent, etc.) and enter a dollar amount
  System stores these budget limits in the database
  User interaction:
  Simple form with dropdown menu for category selection
  Text input field for budget amount
  Save button to store the budget
  Technical requirements:
  Database table to store: user_id, category, budget_amount, time_period
  Form validation to ensure positive numbers
  Backend route to handle budget creation
- Task 9: Progress Bar Implementation
  What it does:
  Calculates percentage of budget used based on transaction data
  Displays visual progress bar showing spending vs. limit
  Shows dollar amounts (spent, remaining, total)
  How it works:
  Query database for all transactions in selected category for current month
  Sum transaction amounts
  Calculate: (total_spent / budget_limit) × 100 = percentage
  Display progress bar filled to that percentage
  Visual elements:
  Progress bar (CSS or Bootstrap component)
  Text showing "$X of $Y spent"
  Text showing "$Z remaining"
  Color coding: green (under 70%), yellow (70-90%), red (over 90%)
  Summary: These stories address monthly and annual financial planning, user-defined savings goals, and system alerts when overspending.
  # Budgeting & Alerts Module – Qiao Huang (Tasks 8 & 9)
This submodule is part of the **Personal Finance Tracker** developed by Team Paldea for IST 303 Fall 2025.

Personal Finance Tracker – Budgeting & Progress (Tasks 8 & 9)

IST 303 – Fall 2025
Developed by: Qiao Huang (Team Paldea)

⸻

📌 Project Overview

This is a Flask-based web app that fulfills:
	•	✅ Task 8 – Budget Input Feature
	•	✅ Task 9 – Budget Progress Visualization

The app allows users to:
	•	Set monthly budgets by category
	•	Automatically track transaction totals
	•	View a visual progress bar (color-coded) showing how much of the budget has been spent

⸻

🚀 Features

✅ Task 8: Monthly Budget Form
	•	Users enter a category and budget amount.
	•	Entries are saved to a SQLite database (budgets table).

✅ Task 9: Budget Progress Bar
	•	Simulated transaction data (in transactions table).
	•	Displays spending per category.
	•	Progress bar colors:
	•	Green = under 70%
	•	Yellow = 70–90%
	•	Red = over 90%

⸻

🧱 Tech Stack
	•	Python 3.8+
	•	Flask 2.3.2
	•	SQLite (local database)
	•	Bootstrap 5 (for progress bar styling)

⸻

📁 File Structure

final_task_8_9_complete/
├── app/
│   ├── __init__.py           # Flask app setup
│   ├── routes.py            # App logic & routing
│   └── templates/
│       ├── budget.html      # Budget entry form
│       └── summary.html     # Progress bar view
├── run.py                   # App entry point
├── requirements.txt         # Flask dependency
├── README.md                # Project documentation (this file)


⸻

🧪 How to Run the Application (Detailed Steps)

📥 Step 1: Download and unzip
	•	Download the ZIP file: final_task_8_9_complete.zip
	•	Unzip it to a location you can find, like your Desktop or Downloads folder

🧭 Step 2: Open Terminal and navigate to the project folder

cd ~/Downloads/final_task_8_9_complete  # Or wherever you unzipped it

🛠️ Step 3: Set up your virtual environment

python3 -m venv venv
source venv/bin/activate

You should now see (venv) at the start of your terminal prompt

📦 Step 4: Install the required packages

pip install -r requirements.txt

This installs Flask so the app can run

🚀 Step 5: Start the app

python run.py

You should see:

 * Running on http://127.0.0.1:5000/

🌐 Step 6: Open the app in your browser
	•	Go to: http://127.0.0.1:5000/budget → to add budgets
	•	Go to: http://127.0.0.1:5000/summary → to view progress bar

⸻

🧠 Lessons Learned
	•	How to use Flask with SQLite for local data persistence
	•	How to structure routes and templates for dynamic views
	•	How to visualize data with Bootstrap progress bars

⸻

📌 Author Contribution

This version was developed specifically to fulfill Tasks 8 and 9 of the IST 303 course:
	•	All Flask routes, HTML templates, and progress logic implemented by: Qiao Huang





### Epic 2.2: Budgeting & Alerts Continued
(Allocated to Rachan)
Linked User Stories: 3, 4, 14
Summary: These stories address monthly and annual financial planning, user-defined savings goals, and system alerts when overspending.

- Task 10: Show alert when budget is exceeded. (Directly supports Story 4: alerts for overspending)
- Task 11: Create goal-setting form for savings/investments/loans. (Supports Story 14: annual financial targets)
- Task 12: Implement progress markers toward goals. (Supports Story 14: tracking goal achievement)

### Epic 3: Visualization & Reporting
(Allocated to Manish)
Linked User Stories: 2, 5
Summary: These stories highlight the need for financial summaries, filters, and visualizations to help users interpret their financial data.

- Task 13: Integrate Chart.js for category spending pie chart. (Supports Story 2: financial dashboard, Story 5: custom filters with summaries)
- Task 14: Add monthly income vs. expense bar chart. (Supports Story 2: monthly budget & summaries)
- Task 15: Implement filters by date (week, month, year). (Supports Story 5: trace financial progress over time)
- Task 16: Generate summary dashboard (income, expenses, cash flow). (Supports Story 2: accessible financial dashboard)
