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
4. [Installation & Setup](#installation--setup)
5. [Project Structure](#project-structure)

---

## 🔗 Overview

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

## Installation & Setup
Prerequisites
Python 3.8 or higher
pip (Python package manager)
Steps
Extract/Download the project folder:

cd smart-finance-insights
Install dependencies:

pip install -r requirements.txt
Initialize the database (creates tables + sample data):

python init_db.py
This creates finance.db with a demo user and comprehensive sample data (6 months of transactions, budgets, investments, goals, notifications).

Start the application:

python app.py
Open in browser:

http://localhost:5000

