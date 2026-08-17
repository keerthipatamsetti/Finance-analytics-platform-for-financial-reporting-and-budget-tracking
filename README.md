# Finance analytics platform for financial reporting and budget tracking

Smart Finance Insights is a web-based personal finance management and analytics platform designed to help users manage their income, expenses, budgets, savings, investments, and overall financial health in one centralized application. The system also provides AI-based financial insights and a Jarvis Chat Assistant to help users understand their financial information and make better financial decisions built with **Python Flask + SQLite + Jinja2 templates**.


![SmartFinance](https://img.shields.io/badge/SmartFinance-Insights-brightgreen)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Flask](https://img.shields.io/badge/Flask-3.x-green)

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Technology Stack](#technology-stack)
4. [Project Structure](#project-structure)
5. [Module Documentation](#module-documentation)

---

## Overview

Smart Finance Insights provides a centralized platform for recording, managing, analysing, and visualizing personal financial information. Users can maintain their financial transactions, create budgets and saving goals, manage investments, analyse spending patterns, monitor financial health, and generate reports.

The application combines financial management, data analytics, visualization, investment analysis, reporting, and AI-based assistance into one web application.


---

## Features

### 🟢 Milestone 1 – Core Finance Management

| **Feature** | **Description** |
|---|---|
| **User Authentication** | Registration, Login, Logout with password hashing |
| **Profile Management** | View/edit user profile |
| **Expense Tracking** | Add/Edit/Delete income and expenses with categorization |
| **Categories** | Food, Shopping, Bills, Entertainment, Transport, Health, Education, Other |
| **Budget Planning** | Create monthly budgets and track utilization |
| **Financial Dashboard** | Summary cards, charts, and recent transactions |
| **Transaction History** | Filter transactions by type, category, month, and year |
| **AI Spending Analysias**|Expense percentage,basic suggestions|

---

### 🟡 Milestone 2 – Investment Tracking & Goal Planning

| **Feature** | **Description** |
|---|---|
| **Investment Portfolio** | Add/Edit/Delete investments (Stocks, Mutual Funds, Gold, FD, Bonds, Real Estate, Crypto) |
| **Profit/Loss Calculation** | Automatic P/L and Return on Investment (ROI) per investment |
| **Asset Allocation** | Visual pie chart of portfolio distribution |
| **Portfolio Analytics Dashboard** | Total invested, current value, growth charts, risk analysis |
| **Top/Low Performers** | Identify best and worst performing assets |
| **Financial Goal Planning** |	Create goals (Emergency Fund, Vacation, Home, Retirement, etc.) |
| **Goal Progress Tracking** |	Completion %, remaining amount, days left, status (On Track/Behind/Achieved) |
| **Goal Contributions** |	Add savings contributions to any goal | 

---

### 🔵 Milestone 3 – Intelligence & Insights

| **Feature** | **Description** |
|---|---|
| **Spending Pattern Analysis**	| Category-wise breakdown, monthly trends, high-spending detection |
| **Budget Recommendations** |	AI-generated personalized budget suggestions based on spending history |
| **Financial Health Score** |	0-100 score with status (Excellent/Good/Fair/Poor) |
| **Health Indicators** | Savings Ratio, Expense Ratio, Investment Growth, Debt-to-Income, Emergency Fund coverage |
| **Alert & Notification System** |	Auto-generated alerts: budget exceeded, bill reminders, goal milestones, investment updates, low balance |
| **AI-Based Financial Insights** |	Personalized recommendations: savings tips, investment suggestions, spending warnings |
| **Intelligence Dashboard** |	Combined view of all analytics, recommendations, score, and notifications |
---

### 🟣 Milestone 4 – Reporting & Analytics

| **Feature** | **Description** |
|---|---|
| **Advanced Financial Reports** |	4 report types: Monthly Expense, Budget Utilization, Investment Performance, Goal Progress |
| **PDF Export** |	Download any report as a professionally formatted PDF |
| **Excel Export** |	Download any report as a styled Excel (.xlsx) spreadsheet |
| **Dashboard Optimization** |	Optimized SQL queries, efficient data loading, summary cards |
| **JARVIS AI Assistant** |	Interactive chatbot that answers finance queries in natural language |
| **JARVIS Capabilities** |	Expense summary, budget recommendations, investment analysis, goal tracking, health score, financial insights |
| **Security** |	Password hashing, input validation, session management, SQL injection prevention (parameterized queries) |

---

##  Technology Stack
| **Component** | **Technology** |
|---|---|
| **Backend** |	Python 3.8+ / Flask 3.x |
| **Database** |	SQLite (via Python's sqlite3 module) |
| **Templating** | Jinja2 (Flask built-in) |
| **Frontend** |	HTML5, CSS3, JavaScript (vanilla) |
| **Charts** |	Chart.js v4 (CDN) |
| **Icons** |	Bootstrap Icons (CDN) |
| **Fonts** | Google Fonts - Inter (CDN) |
| **PDF Export** |	fpdf2 |
| **Excel Export** |	openpyxl |

---

## Project Structure
```
smart-finance-insights/
├── app.py                      # Main Flask application & route registration
├── config.py                   # Configuration (DB path, secret key, etc.)
├── init_db.py                  # Database initialization & sample data seeding
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── finance.db                  # SQLite database (auto-created)
│
├── modules/                    # All business logic (Flask Blueprints)
│   ├── __init__.py
│   ├── auth.py                 # User auth: register, login, logout, profile
│   ├── expenses.py             # Income & expense transaction management
│   ├── budget.py               # Monthly budget planning & monitoring
│   ├── investments.py          # Investment portfolio + portfolio analytics
│   ├── goals.py                # Financial goal planning & tracking
│   ├── dashboard.py            # Main dashboard (combines all data)
│   ├── intelligence.py         # Analysis, recommendations, insights, health routes
│   ├── analysis.py             # Spending pattern analysis engine
│   ├── insights.py             # AI-based financial insights generator
│   ├── health_score.py         # Financial health score calculator
│   ├── notifications.py        # Alert & notification system
│   ├── reports.py              # Financial reports (4 types)
│   ├── export.py               # PDF & Excel export functionality
│   └── jarvis.py               # JARVIS AI Financial Assistant chatbot
│
├── utils/                      # Utility functions
│   ├── __init__.py
│   ├── db.py                   # Database connection helpers
│   └── helpers.py              # Currency formatting, auth decorator, etc.
│
├── templates/                  # Jinja2 HTML templates (18 pages)
│   ├── base.html               # Base layout with sidebar navigation
│   ├── login.html              # Login page
│   ├── register.html           # Registration page
│   ├── profile.html            # User profile management
│   ├── dashboard.html          # Main financial dashboard
│   ├── expenses.html           # Transaction management
│   ├── budget.html             # Budget planner
│   ├── investments.html        # Investment portfolio
│   ├── goals.html              # Financial goals
│   ├── analysis.html           # Spending pattern analysis
│   ├── budget_recommendations.html  # AI budget recommendations
│   ├── insights.html           # AI financial insights
│   ├── health_score.html       # Financial health score
│   ├── notifications.html      # Alerts & notifications
│   ├── reports.html            # Financial reports (4 types)
│   ├── portfolio_analytics.html # Portfolio analytics dashboard
│   ├── jarvis.html             # JARVIS chatbot interface
│   └── error.html              # Error pages (404/500)
│
├── static/                     # Static assets
│   ├── css/
│   │   └── style.css           # Complete stylesheet (green theme)
│   └── js/
│       └── main.js             # JavaScript (charts, modals, JARVIS chat)
│
└── exports/                    # Generated PDF/Excel reports (auto-created)
```
## Module Documentation

### Authentication (`modules/auth.py`)
- `POST /register` — Create new user account
- `POST /login` — Authenticate user, create session
- `GET /logout` — Clear session
- `GET/POST /profile` — View/edit profile
- `POST /change-password` — Change password

### Expenses (`modules/expenses.py`)
- `GET /expenses` — List transactions (with filters)
- `POST /expenses/add` — Add income or expense
- `POST /expenses/edit/<id>` — Edit transaction
- `POST /expenses/delete/<type>/<id>` — Delete transaction
- `GET /api/transaction/<id>` — Get transaction (AJAX)

### Budget (`modules/budget.py`)
- `GET /budget` — View budgets with utilization
- `POST /budget/add` — Add/update budget
- `POST /budget/delete/<id>` — Delete budget

### Investments (`modules/investments.py`)
- `GET /investments` — Portfolio with P/L, ROI, allocation
- `POST /investments/add` — Add investment
- `POST /investments/edit/<id>` — Edit investment
- `POST /investments/delete/<id>` — Delete investment
- `GET /portfolio-analytics` — Analytics dashboard with growth charts & risk

### Goals (`modules/goals.py`)
- `GET /goals` — List goals with progress
- `POST /goals/add` — Create goal
- `POST /goals/edit/<id>` — Edit goal
- `POST /goals/contribute/<id>` — Add savings to goal
- `POST /goals/delete/<id>` — Delete goal

### Intelligence (`modules/intelligence.py` + analysis/insights/health_score)
- `GET /analysis` — Spending pattern analysis
- `GET /budget-recommendations` — AI budget recommendations
- `GET /insights` — AI financial insights
- `GET /health-score` — Financial health score

### Notifications (`modules/notifications.py`)
- `GET /notifications` — View all notifications (auto-generates new ones)
- `POST /notifications/<id>/mark-read` — Mark as read
- `POST /notifications/mark-all-read` — Mark all as read
- `POST /notifications/<id>/delete` — Delete notification
- `GET /api/notifications/count` — Count for badge (AJAX)

### Reports & Export (`modules/reports.py` + `modules/export.py`)
- `GET /reports?type=expense|budget|investment|goal` — View report
- `GET /export/pdf/<type>` — Download PDF
- `GET /export/excel/<type>` — Download Excel

### JARVIS AI Assistant (`modules/jarvis.py`)
- `GET /jarvis` — Chat interface
- `POST /jarvis/chat` — Send message, get AI response
- `POST /jarvis/clear` — Clear chat history

---
