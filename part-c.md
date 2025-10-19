# Part C: Team Member Tasks Presentation

This document showcases the tasks assigned to each team member for the Personal Finance Tracker project, based on the epics and tasks outlined in the README.md.

## Samantha Aguirre
**Epic 1.2: Core Transaction Management Continued**  
Linked User Stories: 1, 6, 7  
Summary: These stories describe the need for a unified system where users can record and categorize both income and expense transactions without relying on multiple services.

- **Task 5:** Categorize transactions by income/expense type. (Supports Stories 6 & 7)
- **Task 6:** Display transactions in a list view. (Supports Stories 6 & 7)
- **Task 7:** Implement delete/edit transaction functionality. (Enhances Stories 6 & 7 usability)

## Gerves Francois Baniakina
**Epic 1: Core Transaction Management**  
Linked User Stories: 1, 6, 7  
Summary: These stories describe the need for a unified system where users can record and categorize both income and expense transactions without relying on multiple services.

- **Task 1:** Set up user authentication (login, register). (Supports Story 1: unified financial system with no extra signups)
- **Task 2:** Create database schema (users, transactions, categories). (Foundation for Stories 6 & 7)
- **Task 3:** Implement “Add income transaction” form. (Supports Story 6: income tracker)
- **Task 4:** Implement “Add expense transaction” form. (Supports Story 7: expense tracker)

## Qiao Huang
**Epic 2: Budgeting & Alerts**  
Linked User Stories: 3, 4, 14

- **Task 8: Monthly Budget Feature**  
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

- **Task 9: Progress Bar Implementation**  
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

## Rachan Sailamai
**Epic 2.2: Budgeting & Alerts Continued**  
Linked User Stories: 3, 4, 14  
Summary: These stories address monthly and annual financial planning, user-defined savings goals, and system alerts when overspending.

- **Task 10:** Show alert when budget is exceeded. (Directly supports Story 4: alerts for overspending)
- **Task 11:** Create goal-setting form for savings/investments/loans. (Supports Story 14: annual financial targets)
- **Task 12:** Implement progress markers toward goals. (Supports Story 14: tracking goal achievement)

## Manish Shrivastav
**Epic 3: Visualization & Reporting**  
Linked User Stories: 2, 5  
Summary: These stories highlight the need for financial summaries, filters, and visualizations to help users interpret their financial data.

- **Task 13:** Integrate Chart.js for category spending pie chart. (Supports Story 2: financial dashboard, Story 5: custom filters with summaries)
- **Task 14:** Add monthly income vs. expense bar chart. (Supports Story 2: monthly budget & summaries)
- **Task 15:** Implement filters by date (week, month, year). (Supports Story 5: trace financial progress over time)
- **Task 16:** Generate summary dashboard (income, expenses, cash flow). (Supports Story 2: accessible financial dashboard)
