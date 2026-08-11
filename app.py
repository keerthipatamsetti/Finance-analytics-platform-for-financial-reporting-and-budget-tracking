from flask import Flask, render_template, request, redirect, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask import send_file
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
import pandas as pd
import io, os
from datetime import datetime

app = Flask(__name__)
app.secret_key = "smartfinance123"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# User Table
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

class Income(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    source = db.Column(db.String(100))
    amount = db.Column(db.Integer)
    date = db.Column(db.String(20))

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(100))
    amount = db.Column(db.Integer)
    date = db.Column(db.String(20))
    description = db.Column(db.String(200))

class Budget(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    month = db.Column(db.String(20), nullable=False)

class Investment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    asset = db.Column(db.String(100))
    investment_name = db.Column(db.String(100))
    purchase_date = db.Column(db.String(20))
    invested_amount = db.Column(db.Float)
    current_value = db.Column(db.Float)

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    notification_type = db.Column(db.String(100))
    message = db.Column(db.String(300))
    priority = db.Column(db.String(20))
    status = db.Column(db.String(20))

class ChatHistory(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    question = db.Column(db.String(500))

    answer = db.Column(db.String(1000))

    date = db.Column(db.String(50))

class Feedback(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    rating = db.Column(
        db.Integer,
        nullable=False
    )

    feedback = db.Column(
        db.Text,
        nullable=False
    )

    date = db.Column(
        db.DateTime,
        default=datetime.now
    )
    
with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return redirect('/login')

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        user = User(name=name,email=email,password=password)
        db.session.add(user)
        db.session.commit()

        return redirect('/login?registered=1')

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        user = User.query.filter_by(
            email=email,
            password=password
        ).first()

        if user:

            session.clear()

            session['user_id'] = user.id
            session['user_name'] = user.name
            session['user_email'] = user.email

            session.modified = True

            print("LOGIN SUCCESS")
            print("USER ID:", session.get('user_id'))
            print("SESSION:", dict(session))

            flash(
                f"Welcome, {user.name}! Login Successful.",
                "success"
            )

            return redirect('/dashboard')

        flash("Invalid email or password.", "danger")

        return redirect('/login')

    return render_template('login.html')



@app.route('/dashboard')
def dashboard():

    # Income & Expense
    total_income = db.session.query(db.func.sum(Income.amount)).scalar() or 0
    total_expense = db.session.query(db.func.sum(Expense.amount)).scalar() or 0
    total_savings = total_income - total_expense

    incomes = Income.query.order_by(Income.id.desc()).limit(5).all()
    expenses = Expense.query.order_by(Expense.id.desc()).limit(5).all()

    # Investments
    investments = Investment.query.all()

    # =========================
    # PORTFOLIO GROWTH DATA
    # =========================

    portfolio_labels = []
    portfolio_values = []

    for investment in investments:

        portfolio_labels.append(
            investment.investment_name
        )

        portfolio_values.append(
            investment.current_value
        )
    total_investment = sum(i.invested_amount for i in investments)
    total_current = sum(i.current_value for i in investments)

    total_profit = total_current - total_investment
    total_assets = len(investments)

    if total_investment > 0:
        overall_roi = round((total_profit / total_investment) * 100, 2)
    else:
        overall_roi = 0

    # Asset Allocation
    asset_dict = {}

    for i in investments:
        asset_dict[i.asset] = asset_dict.get(i.asset, 0) + i.current_value

    asset_labels = list(asset_dict.keys())
    asset_values = list(asset_dict.values())

    # =========================
    # PORTFOLIO GROWTH DATA
    # =========================

    growth_investments = sorted(
        investments,
        key=lambda x: x.purchase_date or ""
    )

    growth_labels = [
        i.purchase_date or "Unknown"
        for i in growth_investments
    ]

    growth_values = [
        i.current_value or 0
        for i in growth_investments
    ]
    # =========================
    # EXPENSE CATEGORY ANALYSIS
    # =========================

    expense_category_dict = {}

    all_expenses = Expense.query.all()

    for expense in all_expenses:

        category = expense.category

        expense_category_dict[category] = (
            expense_category_dict.get(category, 0)
            + expense.amount
        )

    expense_category_labels = list(
        expense_category_dict.keys()
    )

    expense_category_values = list(
        expense_category_dict.values()
    )

    # Top & Worst Asset
    top_asset = "No Data"
    worst_asset = "No Data"

    if investments:
        profits = []

        for i in investments:
            profits.append(
                (
                    i.investment_name,
                    i.current_value - i.invested_amount
                )
            )

        top_asset = max(
            profits,
            key=lambda x: x[1]
        )[0]

        worst_asset = min(
            profits,
            key=lambda x: x[1]
        )[0]

    # Risk Level
    if overall_roi < 10:
        risk_level = "High"
    elif overall_roi < 20:
        risk_level = "Medium"
    else:
        risk_level = "Low"


    # Goal
    goal_amount = 500000

    if total_current >= goal_amount:
        goal_progress = 100
    else:
        goal_progress = round((total_current / goal_amount) * 100, 1)

    # Financial Health Score
    if total_income > 0:
        health_score = round((total_income / (total_income + total_expense)) * 100)
    else:
        health_score = 0

    if health_score > 100:
        health_score = 100

    if health_score < 0:
        health_score = 0

    # AI Recommendation
    if health_score >= 80:
        recommendation = "Excellent Financial Health"
    elif health_score >= 60:
        recommendation = "Good. Try increasing your savings."
    elif health_score >= 40:
        recommendation = "Average. Reduce unnecessary expenses."
    else:
        recommendation = "Poor Financial Health. Control your spending."


    current_month = datetime.now().strftime("%Y-%m")

    monthly_income = 0
    monthly_expense = 0

    for income in Income.query.all():

       if str(income.date).startswith(current_month):
           monthly_income += income.amount


    for expense in Expense.query.all():

       if str(expense.date).startswith(current_month):
           monthly_expense += expense.amount


    monthly_savings = monthly_income - monthly_expense


# =========================
# EXPENSE CATEGORY ANALYSIS
# =========================

    expense_category_dict = {}

    for expense in Expense.query.all():

       category = expense.category

       expense_category_dict[category] = (
         expense_category_dict.get(category, 0)
         + expense.amount
       )


    expense_category_labels = list(
       expense_category_dict.keys()
    )

    expense_category_values = list(
       expense_category_dict.values()
    )


# =========================
# SAVINGS RATE
# =========================

    if total_income > 0:

       savings_rate = round(
         (total_savings / total_income) * 100,
          2
      )

    else:

        savings_rate = 0


# =========================
# FINANCIAL STATUS
# =========================

    if total_savings > 0:

        financial_status = "Positive"

    elif total_savings == 0:

        financial_status = "Balanced"

    else:

        financial_status = "Needs Attention"

    # Notifications
    notifications = Notification.query.order_by(Notification.id.desc()).limit(5).all()
    notification_count = Notification.query.count()

    return render_template(
        "dashboard.html",
        total_income=total_income,
        total_expense=total_expense,
        total_savings=total_savings,
        incomes=incomes,
        expenses=expenses,
        investments=investments,
        total_investment=total_investment,
        total_current=total_current,
        total_profit=total_profit,
        total_assets=total_assets,
        overall_roi=overall_roi,
        asset_labels=asset_labels,
        asset_values=asset_values,
        growth_labels=growth_labels,
        growth_values=growth_values,
        portfolio_labels=portfolio_labels,
        portfolio_values=portfolio_values,
        expense_category_labels=expense_category_labels,
        expense_category_values=expense_category_values,
        top_asset=top_asset,
        worst_asset=worst_asset,
        risk_level=risk_level,
        goal_amount=goal_amount,
        goal_progress=goal_progress,
        health_score=health_score,
        recommendation=recommendation,
        notifications=notifications,
        notification_count=notification_count,
        monthly_income=monthly_income,

        monthly_expense=monthly_expense,

        monthly_savings=monthly_savings,

        savings_rate=savings_rate,

        financial_status=financial_status
    )

# ==========================================================
# SUBMIT FEEDBACK
# ==========================================================

@app.route("/submit_feedback", methods=["POST"])
def submit_feedback():

    rating = request.form.get("rating")
    feedback_text = request.form.get(
        "feedback",
        ""
    ).strip()

    if not rating or not feedback_text:

        return redirect("/dashboard")

    new_feedback = Feedback(

        rating=int(rating),

        feedback=feedback_text

    )

    db.session.add(new_feedback)

    db.session.commit()

    return redirect(
        "/dashboard?feedback=success"
    )

@app.route('/income', methods=['GET', 'POST'])
def income():

    if request.method == 'POST':
        source = request.form['source']
        amount = request.form['amount']
        date = request.form['date']

        new_income = Income(
            source=source,
            amount=amount,
            date=date
        )

        db.session.add(new_income)
        db.session.commit()

        return redirect('/income')

    incomes = Income.query.all()

    return render_template(
        'income.html',
        incomes=incomes
    )

@app.route('/expense', methods=['GET', 'POST'])
def expense():
    if request.method == 'POST':
        category = request.form['category']
        amount = request.form['amount']
        date = request.form['date']

        new_expense = Expense(
            category=category,
            amount=amount,
            date=date
        )

        db.session.add(new_expense)
        db.session.commit()

        return redirect('/dashboard')

    return render_template('expense.html')

@app.route('/profile')
def profile():

    if 'user_id' not in session:
        return redirect('/login')
    
    user = User.query.get(session['user_id'])

    return render_template(
        'profile.html',
        user=user
    )

@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():

    if 'user_id' not in session:
        return redirect('/login')

    user = User.query.get(session['user_id'])

    if request.method == 'POST':

        user.name = request.form['name']
        db.session.commit()

        return redirect('/profile')

    return render_template('edit_profile.html', user=user)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route('/settings')
def settings():

    if 'user_id' not in session:
        return redirect('/login')

    user = User.query.get(session['user_id'])

    return render_template(
        'settings.html',
        user=user
    )

@app.route('/reports')
def reports():

    # =========================
    # INCOME
    # =========================

    total_income = db.session.query(
        db.func.sum(Income.amount)
    ).scalar() or 0


    # =========================
    # EXPENSE
    # =========================

    total_expense = db.session.query(
        db.func.sum(Expense.amount)
    ).scalar() or 0


    # =========================
    # SAVINGS
    # =========================

    total_savings = total_income - total_expense


    # =========================
    # BUDGET
    # =========================

    total_budget = db.session.query(
        db.func.sum(Budget.amount)
    ).scalar() or 0


    # =========================
    # BUDGET UTILIZATION
    # =========================

    if total_budget > 0:

        budget_utilization = round(
            (total_expense / total_budget) * 100,
            2
        )

    else:

        budget_utilization = 0


    # =========================
    # BUDGET STATUS
    # =========================

    if total_budget == 0:

        budget_status = "No Budget Set"

    elif total_expense <= total_budget:

        budget_status = "Within Budget"

    else:

        budget_status = "Over Budget"


    # =========================
    # EXPENSE CATEGORY ANALYSIS
    # =========================

    category_query = db.session.query(
        Expense.category,
        db.func.sum(Expense.amount)
    ).group_by(
        Expense.category
    ).all()


    expense_labels = []
    expense_values = []


    for category, amount in category_query:

        expense_labels.append(category)
        expense_values.append(amount)


    # =========================
    # INVESTMENT ANALYSIS
    # =========================

    total_investment = db.session.query(
        db.func.sum(Investment.invested_amount)
    ).scalar() or 0


    current_value = db.session.query(
        db.func.sum(Investment.current_value)
    ).scalar() or 0


    investment_profit = current_value - total_investment


    if total_investment > 0:

        investment_roi = round(
            (investment_profit / total_investment) * 100,
            2
        )

    else:

        investment_roi = 0


    # =========================
    # FINANCIAL HEALTH
    # =========================

    if total_income > 0:

        health_score = round(
            (total_income /
             (total_income + total_expense)) * 100
        )

    else:

        health_score = 0


    if health_score > 100:
        health_score = 100


    # =========================
    # GOAL PROGRESS
    # =========================

    goal_amount = session.get(
        "goal_amount",
        0
    )


    if goal_amount > 0:

        goal_progress = round(
            (current_value / goal_amount) * 100,
            1
        )

        if goal_progress > 100:
            goal_progress = 100

    else:

        goal_progress = 0


    # =========================
    # RECENT INCOME
    # =========================

    recent_income = Income.query.order_by(
        Income.id.desc()
    ).limit(5).all()


    # =========================
    # RECENT EXPENSES
    # =========================

    recent_expenses = Expense.query.order_by(
        Expense.id.desc()
    ).limit(5).all()


    # =========================
    # FINAL DATA
    # =========================

    return render_template(

        "reports.html",

        total_income=total_income,

        total_expense=total_expense,

        total_savings=total_savings,

        total_budget=total_budget,

        budget_utilization=budget_utilization,

        budget_status=budget_status,

        expense_labels=expense_labels,

        expense_values=expense_values,

        total_investment=total_investment,

        current_value=current_value,

        investment_profit=investment_profit,

        investment_roi=investment_roi,

        health_score=health_score,

        goal_amount=goal_amount,

        goal_progress=goal_progress,

        recent_income=recent_income,

        recent_expenses=recent_expenses

    )

@app.route('/advanced_reports')
def advanced_reports():

    from_date = request.args.get('from_date')
    to_date = request.args.get('to_date')

    incomes = Income.query.all()
    expenses = Expense.query.all()

    # Date filtering
    if from_date:
        incomes = [
            i for i in incomes
            if i.date >= from_date
        ]

        expenses = [
            e for e in expenses
            if e.date >= from_date
        ]

    if to_date:
        incomes = [
            i for i in incomes
            if i.date <= to_date
        ]

        expenses = [
            e for e in expenses
            if e.date <= to_date
        ]

    # Totals
    total_income = sum(i.amount for i in incomes)
    total_expense = sum(e.amount for e in expenses)
    total_savings = total_income - total_expense

    # Category-wise expenses
    category_data = {}

    for e in expenses:

        category_data[e.category] = (
            category_data.get(e.category, 0)
            + e.amount
        )

    categories = list(category_data.keys())
    category_amounts = list(category_data.values())

    # Highest expense category
    if category_data:

        highest_category = max(
            category_data,
            key=category_data.get
        )

        highest_amount = category_data[
            highest_category
        ]

    else:

        highest_category = "No Data"
        highest_amount = 0

    return render_template(
        "advanced_reports.html",

        incomes=incomes,
        expenses=expenses,

        total_income=total_income,
        total_expense=total_expense,
        total_savings=total_savings,

        categories=categories,
        category_amounts=category_amounts,

        highest_category=highest_category,
        highest_amount=highest_amount,

        from_date=from_date or "",
        to_date=to_date or ""
    )

@app.route('/advanced_report_pdf')
def advanced_report_pdf():

    from_date = request.args.get('from_date')
    to_date = request.args.get('to_date')

    incomes = Income.query.all()
    expenses = Expense.query.all()

    if from_date:
        incomes = [
            i for i in incomes
            if i.date >= from_date
        ]

        expenses = [
            e for e in expenses
            if e.date >= from_date
        ]

    if to_date:
        incomes = [
            i for i in incomes
            if i.date <= to_date
        ]

        expenses = [
            e for e in expenses
            if e.date <= to_date
        ]

    total_income = sum(i.amount for i in incomes)
    total_expense = sum(e.amount for e in expenses)
    total_savings = total_income - total_expense

    category_data = {}

    for e in expenses:
        category_data[e.category] = (
            category_data.get(e.category, 0)
            + e.amount
        )

    pdf_buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        pdf_buffer
    )

    styles = getSampleStyleSheet()

    elements = []

    elements.append(
        Paragraph(
            "<b>Advanced Financial Report</b>",
            styles["Title"]
        )
    )

    elements.append(
        Paragraph(
            f"From Date: {from_date or 'All'}",
            styles["Normal"]
        )
    )

    elements.append(
        Paragraph(
            f"To Date: {to_date or 'All'}",
            styles["Normal"]
        )
    )

    elements.append(
        Paragraph(
            f"Total Income: ₹ {total_income}",
            styles["Normal"]
        )
    )

    elements.append(
        Paragraph(
            f"Total Expense: ₹ {total_expense}",
            styles["Normal"]
        )
    )

    elements.append(
        Paragraph(
            f"Total Savings: ₹ {total_savings}",
            styles["Normal"]
        )
    )

    elements.append(
        Paragraph(
            "<b>Category-wise Expenses</b>",
            styles["Heading2"]
        )
    )

    for category, amount in category_data.items():

        elements.append(
            Paragraph(
                f"{category}: ₹ {amount}",
                styles["Normal"]
            )
        )

    elements.append(
        Paragraph(
            "<b>Transactions</b>",
            styles["Heading2"]
        )
    )

    for i in incomes:

        elements.append(
            Paragraph(
                f"Income | {i.date} | "
                f"{i.source} | ₹ {i.amount}",
                styles["Normal"]
            )
        )

    for e in expenses:

        elements.append(
            Paragraph(
                f"Expense | {e.date} | "
                f"{e.category} | ₹ {e.amount}",
                styles["Normal"]
            )
        )

    doc.build(elements)

    pdf_buffer.seek(0)

    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name="Advanced_Financial_Report.pdf",
        mimetype="application/pdf"
    )

@app.route('/advanced_report_excel')
def advanced_report_excel():

    from_date = request.args.get('from_date')
    to_date = request.args.get('to_date')

    incomes = Income.query.all()
    expenses = Expense.query.all()

    if from_date:
        incomes = [
            i for i in incomes
            if i.date >= from_date
        ]

        expenses = [
            e for e in expenses
            if e.date >= from_date
        ]

    if to_date:
        incomes = [
            i for i in incomes
            if i.date <= to_date
        ]

        expenses = [
            e for e in expenses
            if e.date <= to_date
        ]

    rows = []

    for i in incomes:

        rows.append({
            "Date": i.date,
            "Type": "Income",
            "Category / Source": i.source,
            "Amount": i.amount
        })

    for e in expenses:

        rows.append({
            "Date": e.date,
            "Type": "Expense",
            "Category / Source": e.category,
            "Amount": e.amount
        })

    df = pd.DataFrame(rows)

    excel_buffer = io.BytesIO()

    with pd.ExcelWriter(
        excel_buffer,
        engine="openpyxl"
    ) as writer:

        df.to_excel(
            writer,
            index=False,
            sheet_name="Transactions"
        )

        summary = pd.DataFrame({

            "Metric": [
                "Total Income",
                "Total Expense",
                "Total Savings"
            ],

            "Amount": [
                sum(i.amount for i in incomes),
                sum(e.amount for e in expenses),
                sum(i.amount for i in incomes)
                - sum(e.amount for e in expenses)
            ]

        })

        summary.to_excel(
            writer,
            index=False,
            sheet_name="Summary"
        )

    excel_buffer.seek(0)

    return send_file(
        excel_buffer,
        as_attachment=True,
        download_name="Advanced_Financial_Report.xlsx",
        mimetype=
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

@app.route('/download_reports_pdf')
def download_reports_pdf():

    total_income = db.session.query(
        db.func.sum(Income.amount)
    ).scalar() or 0

    total_expense = db.session.query(
        db.func.sum(Expense.amount)
    ).scalar() or 0

    total_savings = total_income - total_expense

    total_budget = db.session.query(
        db.func.sum(Budget.amount)
    ).scalar() or 0

    total_investment = db.session.query(
        db.func.sum(Investment.invested_amount)
    ).scalar() or 0

    current_value = db.session.query(
        db.func.sum(Investment.current_value)
    ).scalar() or 0

    investment_profit = current_value - total_investment

    if total_investment > 0:
        investment_roi = round(
            (investment_profit / total_investment) * 100,
            2
        )
    else:
        investment_roi = 0

    if total_budget > 0:
        budget_utilization = round(
            (total_expense / total_budget) * 100,
            2
        )
    else:
        budget_utilization = 0

    if total_income > 0:
        health_score = round(
            (total_income /
             (total_income + total_expense)) * 100
        )
    else:
        health_score = 0

    # Create PDF in memory
    buffer = io.BytesIO()

    pdf = SimpleDocTemplate(buffer)

    styles = getSampleStyleSheet()

    elements = []

    elements.append(
        Paragraph(
            "<b>Smart Finance Insights</b>",
            styles["Title"]
        )
    )

    elements.append(
        Paragraph(
            "Financial Report",
            styles["Heading2"]
        )
    )

    elements.append(
        Paragraph(
            f"Total Income: ₹{total_income}",
            styles["Normal"]
        )
    )

    elements.append(
        Paragraph(
            f"Total Expenses: ₹{total_expense}",
            styles["Normal"]
        )
    )

    elements.append(
        Paragraph(
            f"Total Savings: ₹{total_savings}",
            styles["Normal"]
        )
    )

    elements.append(
        Paragraph(
            f"Total Budget: ₹{total_budget}",
            styles["Normal"]
        )
    )

    elements.append(
        Paragraph(
            f"Budget Utilization: {budget_utilization}%",
            styles["Normal"]
        )
    )

    elements.append(
        Paragraph(
            f"Total Investment: ₹{total_investment}",
            styles["Normal"]
        )
    )

    elements.append(
        Paragraph(
            f"Current Investment Value: ₹{current_value}",
            styles["Normal"]
        )
    )

    elements.append(
        Paragraph(
            f"Investment Profit/Loss: ₹{investment_profit}",
            styles["Normal"]
        )
    )

    elements.append(
        Paragraph(
            f"Investment ROI: {investment_roi}%",
            styles["Normal"]
        )
    )

    elements.append(
        Paragraph(
            f"Financial Health Score: {health_score}/100",
            styles["Normal"]
        )
    )

    pdf.build(elements)

    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name="Financial_Report.pdf",
        mimetype="application/pdf"
    )

# ==========================================
# DOWNLOAD REPORT AS EXCEL
# ==========================================

@app.route('/download_reports_excel')
def download_reports_excel():

    total_income = db.session.query(
        db.func.sum(Income.amount)
    ).scalar() or 0

    total_expense = db.session.query(
        db.func.sum(Expense.amount)
    ).scalar() or 0

    total_savings = total_income - total_expense

    total_budget = db.session.query(
        db.func.sum(Budget.amount)
    ).scalar() or 0

    total_investment = db.session.query(
        db.func.sum(Investment.invested_amount)
    ).scalar() or 0

    current_value = db.session.query(
        db.func.sum(Investment.current_value)
    ).scalar() or 0

    investment_profit = current_value - total_investment

    if total_investment > 0:

        investment_roi = round(
            (investment_profit / total_investment) * 100,
            2
        )

    else:

        investment_roi = 0


    if total_budget > 0:

        budget_utilization = round(
            (total_expense / total_budget) * 100,
            2
        )

    else:

        budget_utilization = 0


    if total_income > 0:

        health_score = round(
            (total_income /
             (total_income + total_expense)) * 100
        )

    else:

        health_score = 0


    # ======================================
    # SUMMARY DATA
    # ======================================

    summary_data = {

        "Metric": [

            "Total Income",
            "Total Expense",
            "Total Savings",
            "Total Budget",
            "Budget Utilization",
            "Total Investment",
            "Current Investment Value",
            "Investment Profit/Loss",
            "Investment ROI",
            "Financial Health Score"

        ],

        "Value": [

            total_income,
            total_expense,
            total_savings,
            total_budget,
            budget_utilization,
            total_investment,
            current_value,
            investment_profit,
            investment_roi,
            health_score

        ]

    }


    df_summary = pd.DataFrame(summary_data)


    # ======================================
    # EXPENSE DATA
    # ======================================

    expenses = Expense.query.all()

    expense_data = []

    for expense in expenses:

        expense_data.append({

            "Category": expense.category,

            "Amount": expense.amount,

            "Date": expense.date,

            "Description": expense.description

        })


    df_expenses = pd.DataFrame(expense_data)


    # ======================================
    # INVESTMENT DATA
    # ======================================

    investments = Investment.query.all()

    investment_data = []

    for investment in investments:

        profit = (
            investment.current_value
            - investment.invested_amount
        )

        if investment.invested_amount > 0:

            roi = round(
                (profit /
                 investment.invested_amount) * 100,
                2
            )

        else:

            roi = 0


        investment_data.append({

            "Asset": investment.asset,

            "Investment Name":
                investment.investment_name,

            "Purchase Date":
                investment.purchase_date,

            "Invested Amount":
                investment.invested_amount,

            "Current Value":
                investment.current_value,

            "Profit/Loss":
                profit,

            "ROI %":
                roi

        })


    df_investments = pd.DataFrame(
        investment_data
    )


    # ======================================
    # CREATE EXCEL FILE
    # ======================================

    output = io.BytesIO()


    with pd.ExcelWriter(
        output,
        engine="openpyxl"
    ) as writer:

        df_summary.to_excel(
            writer,
            index=False,
            sheet_name="Summary"
        )

        df_expenses.to_excel(
            writer,
            index=False,
            sheet_name="Expenses"
        )

        df_investments.to_excel(
            writer,
            index=False,
            sheet_name="Investments"
        )


    output.seek(0)


    return send_file(

        output,

        as_attachment=True,

        download_name="Financial_Report.xlsx",

        mimetype=
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

    )

@app.route('/saving_goals', methods=['GET', 'POST'])
def saving_goals():
    return render_template('saving_goals.html')

@app.route('/budget', methods=['GET', 'POST'])
def budget():

    if request.method == 'POST':

        new_budget = Budget(
            category=request.form['category'],
            amount=float(request.form['amount']),
            month=request.form['month']
        )

        db.session.add(new_budget)
        db.session.commit()

        return redirect('/budget')

    budgets = Budget.query.all()

    total_budget = sum(b.amount for b in budgets)

    total_expense = db.session.query(db.func.sum(Expense.amount)).scalar() or 0

    return render_template(
        'budget.html',
        budgets=budgets,
        budget=total_budget,
        total_expense=total_expense
    )

@app.route('/delete_expense/<int:id>')
def delete_expense(id):
    expense = Expense.query.get(id)
    db.session.delete(expense)
    db.session.commit()
    return redirect('/expense')

@app.route('/delete_income/<int:id>')
def delete_income(id):
    income = Income.query.get(id)
    db.session.delete(income)
    db.session.commit()
    return redirect('/income')

@app.route('/edit_income/<int:id>', methods=['GET', 'POST'])
def edit_income(id):
    income = Income.query.get(id)

    if request.method == 'POST':
        income.source = request.form['source']
        income.amount = request.form['amount']
        income.date = request.form['date']

        db.session.commit()
        return redirect('/income')

    return render_template('edit_income.html', income=income)

@app.route('/edit_expense/<int:id>', methods=['GET', 'POST'])
def edit_expense(id):
    expense = Expense.query.get(id)

    if request.method == 'POST':
        expense.category = request.form['category']
        expense.amount = request.form['amount']
        expense.date = request.form['date']
        expense.description = request.form['description']

        db.session.commit()
        return redirect('/expense')

    return render_template('edit_expense.html', expense=expense)

@app.route('/edit_budget/<int:id>', methods=['GET', 'POST'])
def edit_budget(id):
    budget = Budget.query.get_or_404(id)

    if request.method == 'POST':

        budget.category = request.form['category']
        budget.amount = float(request.form['amount'])
        budget.month = request.form['month']

        db.session.commit()

        return redirect('/budget')

    return render_template('edit_budget.html', budget=budget)


@app.route('/delete_budget/<int:id>')
def delete_budget(id):

    budget = Budget.query.get_or_404(id)

    db.session.delete(budget)
    db.session.commit()

    return redirect('/budget')

@app.route("/ai_insights")
def ai_insights():

    total_income = db.session.query(db.func.sum(Income.amount)).scalar() or 0
    total_expense = db.session.query(db.func.sum(Expense.amount)).scalar() or 0
    total_investment = db.session.query(db.func.sum(Investment.invested_amount)).scalar() or 0
    current_value = db.session.query(db.func.sum(Investment.current_value)).scalar() or 0

    total_savings = total_income - total_expense
    
    
    if total_income > 0:
        health_score = round((total_income / (total_income + total_expense)) * 100)
    else:
        health_score = 0

    if total_investment > 0:
        investment_growth = round(((current_value - total_investment) / total_investment) * 100, 2)
    else:
        investment_growth = 0

    spending_data = [12000,15000,18000,16000,20000,17000]
    investment_data = [50000,55000,62000,70000,76000,82000]

    if health_score >= 80:
        recommendation = "Excellent! Continue saving."
    elif health_score >= 60:
        recommendation = "Good. Reduce unnecessary expenses."
    else:
        recommendation = "Needs Improvement. Increase savings."

    return render_template(
        "ai_insights.html",
        total_income=total_income,
        total_expense=total_expense,
        total_savings=total_savings,
        health_score=health_score,
        investment_growth=investment_growth,
        recommendation=recommendation,
        spending_data=spending_data,
        investment_data=investment_data
    )


@app.route('/investment', methods=['GET', 'POST'])
def investment():

    if request.method == "POST":

        new = Investment(
            asset=request.form['asset'],
            investment_name=request.form['investment_name'],
            purchase_date=request.form['purchase_date'],
            invested_amount=float(request.form['invested_amount']),
            current_value=float(request.form['current_value'])
        )

        db.session.add(new)
        db.session.commit()

        return redirect('/investment')

    search = request.args.get("search")

    if search:
        investments = Investment.query.filter(
            Investment.investment_name.contains(search)
        ).all()
    else:
        investments = Investment.query.all()

    total_investment = sum(i.invested_amount for i in investments)
    total_current = sum(i.current_value for i in investments)
    total_assets = len(investments)

    total_profit = total_current - total_investment

    if total_investment > 0:
        overall_roi = round((total_profit / total_investment) * 100, 2)
    else:
        overall_roi = 0

    return render_template(
        "investment.html",
        investments=investments,
        total_investment=total_investment,
        total_current=total_current,
        total_assets=total_assets,
        total_profit=total_profit,
        overall_roi=overall_roi
    )

       
@app.route('/view_investment/<int:id>')
def view_investment(id):

    investment = Investment.query.get_or_404(id)

    profit = investment.current_value - investment.invested_amount

    if investment.invested_amount > 0:
        roi = round((profit / investment.invested_amount) * 100, 2)
    else:
        roi = 0

    return render_template(
        "view_investment.html",
        investment=investment,
        profit=profit,
        roi=roi
    )

@app.route('/asset_allocation')
def asset_allocation():

    investments = Investment.query.all()

    total_investment = sum(i.invested_amount for i in investments)
    total_current = sum(i.current_value for i in investments)

    total_profit = total_current - total_investment

    if total_investment > 0:
        overall_roi = round((total_profit / total_investment) * 100,2)
    else:
        overall_roi = 0

    asset_dict = {}

    for i in investments:
        asset_dict[i.asset] = asset_dict.get(i.asset,0) + i.current_value

    asset_labels = list(asset_dict.keys())
    asset_values = list(asset_dict.values())

    return render_template(
        "asset_allocation.html",
        investments=investments,
        total_investment=total_investment,
        total_current=total_current,
        total_profit=total_profit,
        overall_roi=overall_roi,
        asset_labels=asset_labels,
        asset_values=asset_values
    )

@app.route('/financial_goals', methods=['GET', 'POST'])
def financial_goals():

    goal_amount = 0

    if request.method == "POST":
        goal_amount = float(request.form['goal_amount'])
        session['goal_amount'] = goal_amount

    goal_amount = session.get("goal_amount", 0)

    total_current = db.session.query(
        db.func.sum(Investment.current_value)
    ).scalar() or 0

    if goal_amount > 0:
        progress = round((total_current / goal_amount) * 100, 1)

        if progress > 100:
            progress = 100
    else:
        progress = 0

    return render_template(
        "financial_goals.html",
        goal_amount=goal_amount,
        total_current=total_current,
        progress=progress
    )

@app.route('/portfolio_analytics')
def portfolio_analytics():

    investments = Investment.query.all()

    total_investment = sum(i.invested_amount for i in investments)
    total_current = sum(i.current_value for i in investments)
    total_profit = total_current - total_investment

    if total_investment > 0:
        overall_roi = round((total_profit / total_investment) * 100, 2)
    else:
        overall_roi = 0

    top_asset = "No Data"
    worst_asset = "No Data"

    if investments:
        profits = [
            (i.investment_name, i.current_value - i.invested_amount)
            for i in investments
        ]

        top_asset = max(profits, key=lambda x: x[1])[0]
        worst_asset = min(profits, key=lambda x: x[1])[0]

    return render_template(
        "portfolio_analytics.html",
        total_investment=total_investment,
        total_current=total_current,
        total_profit=total_profit,
        overall_roi=overall_roi,
        total_assets=len(investments),
        top_asset=top_asset,
        worst_asset=worst_asset
    )

@app.route('/transactions')
def transactions():

    incomes = Income.query.all()
    expenses = Expense.query.all()

    return render_template(
        "transactions.html",
        incomes=incomes,
        expenses=expenses
    )

@app.route('/edit_investment/<int:id>', methods=['GET', 'POST'])
def edit_investment(id):

    investment = Investment.query.get_or_404(id)

    if request.method == "POST":

        investment.asset = request.form['asset']
        investment.investment_name = request.form['investment_name']
        investment.purchase_date = request.form['purchase_date']
        investment.invested_amount = float(request.form['invested_amount'])
        investment.current_value = float(request.form['current_value'])

        db.session.commit()

        return redirect('/investment')

    return render_template(
        "edit_investment.html",
        investment=investment
    )

@app.route('/delete_investment/<int:id>')
def delete_investment(id):

    investment = Investment.query.get_or_404(id)

    db.session.delete(investment)

    db.session.commit()

    return redirect('/investment')



@app.route('/download_pdf')
def download_pdf():

    investments = Investment.query.all()

    pdf = SimpleDocTemplate("Investment_Report.pdf")
    styles = getSampleStyleSheet()

    elements = []

    elements.append(Paragraph("<b>Investment Portfolio Report</b>", styles['Title']))

    for i in investments:

        elements.append(
            Paragraph(
                f"""
                Asset : {i.asset}<br/>
                Investment : {i.investment_name}<br/>
                Invested Amount : ₹{i.invested_amount}<br/>
                Current Value : ₹{i.current_value}<br/><br/>
                """,
                styles['BodyText']
            )
        )

    pdf.build(elements)

    return send_file(
        "Investment_Report.pdf",
        as_attachment=True
    )

@app.route('/download_excel')
def download_excel():

    investments = Investment.query.all()

    data = []

    for i in investments:

        data.append({

            "Asset": i.asset,

            "Investment": i.investment_name,

            "Invested Amount": i.invested_amount,

            "Current Value": i.current_value

        })

    df = pd.DataFrame(data)

    file_name = "Investment_Report.xlsx"

    df.to_excel(file_name, index=False)

    return send_file(
        file_name,
        as_attachment=True
    )

@app.route("/spending_analysis")
def spending_analysis():

    expenses = Expense.query.all()

    total_expense = sum(e.amount for e in expenses)
    
    incomes = Income.query.all()
    total_income = sum(i.amount for i in incomes)

    total_budget = total_income

    categories = {}

    for e in expenses:
        categories[e.category] = categories.get(e.category, 0) + e.amount

    highest_category = "No Data"

    if categories:
        highest_category = max(categories, key=categories.get)

    category_summary = []

    for category, amount in categories.items():

        percentage = round((amount / total_expense) * 100, 2) if total_expense > 0 else 0

        status = "High" if percentage > 30 else "Medium" if percentage > 15 else "Low"

        category_summary.append({
            "category": category,
            "amount": amount,
            "percentage": percentage,
            "status": status
        })

    budget_utilization = round((total_expense / total_budget) * 100, 2) if total_budget > 0 else 0

    if budget_utilization >= 90:
        recommendation = "Warning: You have almost reached your monthly budget."
    elif budget_utilization >= 70:
        recommendation = "Your spending is moderate. Try to reduce unnecessary expenses."
    else:
        recommendation = "Excellent! Your spending is well within your budget."

    return render_template(
        "spending_analysis.html",
        total_expense=total_expense,
        total_budget=total_budget,
        highest_category=highest_category,
        category_summary=category_summary,
        budget_utilization=budget_utilization,
        recommendation=recommendation
    )



@app.route("/budget_recommendation")
def budget_recommendation():

    expenses = Expense.query.all()
    budgets = Budget.query.all()

    total_expense = sum(exp.amount for exp in expenses)
    total_budget = sum(b.amount for b in budgets)

    category_totals = {}

    for exp in expenses:
        if exp.category in category_totals:
            category_totals[exp.category] += exp.amount
        else:
            category_totals[exp.category] = exp.amount

    recommendations = []

    if total_expense > total_budget:
        recommendations.append({
            "title": "Reduce Spending",
            "message": "Your expenses exceeded your budget. Reduce unnecessary spending.",
            "color": "danger"
        })
    else:
        recommendations.append({
            "title": "Good Job",
            "message": "You are spending within your budget.",
            "color": "success"
        })

    recommendations.append({
        "title": "50/30/20 Rule",
        "message": "Allocate 50% for needs, 30% for wants and 20% for savings.",
        "color": "primary"
    })

    return render_template(
        "budget_recommendation.html",
        total_budget=total_budget,
        total_expense=total_expense,
        category_totals=category_totals,
        recommendations=recommendations,
        expenses=expenses,
        budgets=budgets
    )

@app.route("/financial_health")
def financial_health():

    total_income = db.session.query(db.func.sum(Income.amount)).scalar() or 0
    total_expense = db.session.query(db.func.sum(Expense.amount)).scalar() or 0

    savings = total_income - total_expense

    if total_income > 0:
        savings_percentage = (savings / total_income) * 100
    else:
        savings_percentage = 0

    if savings_percentage >= 40:
        score = 95
        status = "Excellent"
    elif savings_percentage >= 20:
        score = 80
        status = "Good"
    elif savings_percentage >= 10:
        score = 60
        status = "Average"
    else:
        score = 40
        status = "Poor"

    return render_template(
        "financial_health.html",
        total_income=total_income,
        total_expense=total_expense,
        savings=savings,
        score=score,
        status=status
    )

@app.route('/notifications', methods=['GET', 'POST'])
def notifications():

    if request.method == "POST":

        new_notification = Notification(
            notification_type=request.form['notification_type'],
            message=request.form['message'],
            priority=request.form['priority'],
            status=request.form['status']
        )

        db.session.add(new_notification)
        db.session.commit()

        return redirect('/notifications')

    notifications = Notification.query.all()

    return render_template(
        "notifications.html",
        notifications=notifications
    )

@app.route("/help")
def help():
    return render_template("help.html")

@app.route('/download_income_excel')
def download_income_excel():

    incomes = Income.query.all()

    data = []

    for income in incomes:
        data.append({
            "ID": income.id,
            "Source": income.source,
            "Amount": income.amount,
            "Date": income.date
        })

    df = pd.DataFrame(data)

    file_name = "Income_Report.xlsx"

    df.to_excel(file_name, index=False)

    return send_file(
        file_name,
        as_attachment=True
    )

@app.route('/download_expense_excel')
def download_expense_excel():

    expenses = Expense.query.all()

    data = []

    for expense in expenses:
        data.append({
            "ID": expense.id,
            "Category": expense.category,
            "Amount": expense.amount,
            "Date": expense.date,
            "Description": expense.description
        })

    df = pd.DataFrame(data)

    file_name = "Expense_Report.xlsx"

    df.to_excel(file_name, index=False)

    return send_file(
        file_name,
        as_attachment=True
    )

@app.route('/download_investment_excel')
def download_investment_excel():

    investments = Investment.query.all()

    data = []

    for investment in investments:
        data.append({
            "ID": investment.id,
            "Asset": investment.asset,
            "Investment Name": investment.investment_name,
            "Purchase Date": investment.purchase_date,
            "Invested Amount": investment.invested_amount,
            "Current Value": investment.current_value
        })

    df = pd.DataFrame(data)

    file_name = "Investment_Report.xlsx"

    df.to_excel(file_name, index=False)

    return send_file(
        file_name,
        as_attachment=True
    )

# ==========================================================
# JARVIS CHAT API - PART 1
# ==========================================================

@app.route("/jarvis_chat", methods=["POST"])
def jarvis_chat():

    data = request.get_json() or {}

    question = str(
        data.get("question", "")
    ).strip()

    q = question.lower()

    # ======================================================
    # FINANCIAL DATA
    # ======================================================

    total_income = db.session.query(
        db.func.sum(Income.amount)
    ).scalar() or 0

    total_expense = db.session.query(
        db.func.sum(Expense.amount)
    ).scalar() or 0

    total_savings = (
        total_income - total_expense
    )

    total_investment = db.session.query(
        db.func.sum(Investment.invested_amount)
    ).scalar() or 0

    current_value = db.session.query(
        db.func.sum(Investment.current_value)
    ).scalar() or 0

    # ======================================================
    # PERCENTAGES
    # ======================================================

    if total_income > 0:

        saving_percent = round(
            (total_savings / total_income) * 100,
            2
        )

        expense_percent = round(
            (total_expense / total_income) * 100,
            2
        )

    else:

        saving_percent = 0
        expense_percent = 0

    # ======================================================
    # FINANCIAL HEALTH
    # ======================================================

    if total_income > 0:

        health_score = round(
            (
                total_income /
                (total_income + total_expense)
            ) * 100
        )

    else:

        health_score = 0

    if health_score >= 80:

        health_status = "Excellent 🟢"

    elif health_score >= 60:

        health_status = "Good 🟡"

    else:

        health_status = "Needs Improvement 🔴"

    # ======================================================
    # ROI
    # ======================================================

    if total_investment > 0:

        profit_loss = (
            current_value -
            total_investment
        )

        roi = round(
            (
                profit_loss /
                total_investment
            ) * 100,
            2
        )

    else:

        profit_loss = 0
        roi = 0

    # ======================================================
    # BUDGET RECOMMENDATION
    # ======================================================

    recommended_budget = round(
        total_income * 0.50
    )

    recommended_savings = round(
        total_income * 0.20
    )

    recommended_investment = round(
        total_income * 0.30
    )

    # ======================================================
    # GREETING
    # ======================================================

    hour = datetime.now().hour

    if hour < 12:

        greeting = "🌞 Good Morning!"

    elif hour < 17:

        greeting = "☀️ Good Afternoon!"

    else:

        greeting = "🌙 Good Evening!"

    # ======================================================
    # ALERTS
    # ======================================================

    alerts = []

    if total_expense > total_income:

        alerts.append(
            "🚨 Expenses are higher than income."
        )

    if health_score < 50:

        alerts.append(
            "⚠️ Financial health score is low."
        )

    if roi < 0:

        alerts.append(
            "📉 Investment portfolio is showing a loss."
        )

    if total_savings < 0:

        alerts.append(
            "⚠️ Your current savings are negative."
        )

    if total_savings > 50000:

        alerts.append(
            "🎉 Excellent savings achievement."
        )

    # ======================================================
    # SMART TIPS
    # ======================================================

    tips = []

    if total_expense > total_income:

        tips.append(
            "Reduce unnecessary expenses."
        )

    else:

        tips.append(
            "Your expenses are within your income."
        )

    if saving_percent < 20:

        tips.append(
            "Try to save at least 20% of your income."
        )

    else:

        tips.append(
            "Your savings rate is healthy."
        )

    if roi < 10:

        tips.append(
            "Review your investment portfolio regularly."
        )

    else:

        tips.append(
            "Your investment returns are performing well."
        )

    if health_score < 60:

        tips.append(
            "Focus on improving your income-to-expense balance."
        )

    # ======================================================
    # CHART
    # ======================================================

    chart = None
    # ======================================================
    # GREETING
    # ======================================================

    if any(word in q for word in [
        "hello",
        "hi",
        "hey",
        "good morning",
        "good afternoon",
        "good evening"
    ]):

        reply = (
            f"{greeting}\n\n"
            "🤖 I am Jarvis, your Smart Financial Assistant.\n\n"
            "Ask me anything about your finances. "
            "I can analyze income, expenses, savings, "
            "budget, investments, ROI and financial health."
        )

    # ======================================================
    # INCOME + EXPENSE
    # ======================================================

    elif (
        any(word in q for word in [
            "income",
            "earn",
            "earning",
            "salary"
        ])
        and
        any(word in q for word in [
            "expense",
            "spending",
            "spent",
            "cost"
        ])
    ):

        reply = (
            "📊 Income & Expense Summary\n\n"
            f"💰 Total Income : ₹{total_income:,.2f}\n"
            f"💸 Total Expense : ₹{total_expense:,.2f}\n"
            f"💵 Total Savings : ₹{total_savings:,.2f}\n\n"
            f"📌 Expense Ratio : {expense_percent}%\n"
            f"📌 Savings Rate : {saving_percent}%"
        )

        chart = {
            "type": "bar",
            "title": "Income vs Expense vs Savings",
            "labels": [
                "Income",
                "Expense",
                "Savings"
            ],
            "values": [
                float(total_income),
                float(total_expense),
                float(total_savings)
            ],
            "label": "Amount"
        }

    # ======================================================
    # INCOME
    # ======================================================

    elif any(word in q for word in [
        "total income",
        "my income",
        "show income",
        "income",
        "earnings",
        "earning",
        "salary",
        "earned",
        "money earned",
        "how much did i earn"
    ]):

        reply = (
            "💰 Income Summary\n\n"
            f"Total Income : ₹{total_income:,.2f}\n\n"
            "This amount represents the total income "
            "recorded in your finance database."
        )

        chart = {
            "type": "bar",
            "title": "Total Income",
            "labels": ["Income"],
            "values": [float(total_income)],
            "label": "Amount"
        }

    # ======================================================
    # EXPENSE
    # ======================================================

    elif any(word in q for word in [
        "total expense",
        "my expense",
        "my expenses",
        "show expense",
        "show expenses",
        "expense",
        "expenses",
        "spending",
        "spent",
        "money spent",
        "how much did i spend"
    ]):

        reply = (
            "💸 Expense Summary\n\n"
            f"Total Expense : ₹{total_expense:,.2f}\n"
            f"Expense Ratio : {expense_percent}%\n\n"
            "This shows how much of your income "
            "is being used for expenses."
        )

        chart = {
            "type": "bar",
            "title": "Total Expense",
            "labels": ["Expense"],
            "values": [float(total_expense)],
            "label": "Amount"
        }

    # ======================================================
    # SAVINGS
    # ======================================================

    elif any(word in q for word in [
        "total savings",
        "my savings",
        "show savings",
        "how much money did i save",
        "how much did i save",
        "how much have i saved",
        "savings",
        "saving",
        "saved",
        "save money"
    ]):

        if total_savings >= 0:

            saving_message = (
                "✅ You currently have positive savings."
            )

        else:

            saving_message = (
                "⚠️ Your expenses are higher than your income, "
                "so your savings are negative."
            )

        reply = (
            "💵 Savings Analysis\n\n"
            f"Total Savings : ₹{total_savings:,.2f}\n"
            f"Savings Rate : {saving_percent}%\n\n"
            f"{saving_message}"
        )

        chart = {
            "type": "bar",
            "title": "Savings Overview",
            "labels": [
                "Income",
                "Expense",
                "Savings"
            ],
            "values": [
                float(total_income),
                float(total_expense),
                float(total_savings)
            ],
            "label": "Amount"
        }

    # ======================================================
    # OVERSPENDING
    # ======================================================

    elif any(word in q for word in [
        "am i overspending",
        "overspending",
        "spending more than i earn",
        "spending more than my income",
        "more than i earn",
        "more than i make",
        "am i spending too much",
        "expense analysis"
    ]):

        if total_expense > total_income:

            difference = (
                total_expense -
                total_income
            )

            reply = (
                "🚨 Overspending Analysis\n\n"
                "Yes, you are spending more than you earn.\n\n"
                f"💰 Income : ₹{total_income:,.2f}\n"
                f"💸 Expense : ₹{total_expense:,.2f}\n"
                f"⚠️ Excess Spending : ₹{difference:,.2f}\n\n"
                "Recommendation: Reduce unnecessary expenses "
                "and review your monthly budget."
            )

        else:

            remaining = (
                total_income -
                total_expense
            )

            reply = (
                "✅ Overspending Analysis\n\n"
                "No, you are not spending more than you earn.\n\n"
                f"💰 Income : ₹{total_income:,.2f}\n"
                f"💸 Expense : ₹{total_expense:,.2f}\n"
                f"💵 Remaining : ₹{remaining:,.2f}\n\n"
                "Your expenses are currently within your income."
            )

        chart = {
            "type": "bar",
            "title": "Income vs Spending",
            "labels": [
                "Income",
                "Expense"
            ],
            "values": [
                float(total_income),
                float(total_expense)
            ],
            "label": "Amount"
        }

    # ======================================================
    # HIGHEST EXPENSE CATEGORY
    # ======================================================

    elif any(word in q for word in [
        "highest expense",
        "highest category",
        "most spending",
        "maximum expense",
        "top expense",
        "where am i spending the most",
        "where am i spending",
        "which category costs the most",
        "biggest expense"
    ]):

        categories = db.session.query(
            Expense.category,
            db.func.sum(
                Expense.amount
            ).label("total")
        ).group_by(
            Expense.category
        ).order_by(
            db.desc("total")
        ).all()

        if categories:

            highest = categories[0]

            reply = (
                "📊 Highest Expense Category\n\n"
                f"🏆 Category : {highest.category}\n"
                f"💸 Amount : ₹{highest.total:,.2f}\n\n"
                "This is the category where you "
                "are spending the most money."
            )

            chart = {
                "type": "doughnut",
                "title": "Expense by Category",
                "labels": [
                    str(row.category)
                    for row in categories
                ],
                "values": [
                    float(row.total)
                    for row in categories
                ],
                "label": "Expense"
            }

        else:

            reply = (
                "No expense records are available "
                "to identify the highest category."
            )

    # ======================================================
    # LOWEST EXPENSE CATEGORY
    # ======================================================

    elif any(word in q for word in [
        "lowest expense",
        "lowest category",
        "minimum expense",
        "least spending",
        "smallest expense",
        "category has the lowest",
        "which category has the lowest expense"
    ]):

        lowest = db.session.query(
            Expense.category,
            db.func.sum(
                Expense.amount
            ).label("total")
        ).group_by(
            Expense.category
        ).order_by(
            db.asc("total")
        ).first()

        if lowest:

            reply = (
                "📉 Lowest Expense Category\n\n"
                f"Category : {lowest.category}\n"
                f"Amount : ₹{lowest.total:,.2f}\n\n"
                "This is currently your lowest "
                "expense category."
            )

            chart = {
                "type": "bar",
                "title": "Lowest Expense Category",
                "labels": [
                    str(lowest.category)
                ],
                "values": [
                    float(lowest.total)
                ],
                "label": "Expense"
            }

        else:

            reply = (
                "No expense records are available "
                "to identify the lowest category."
            )

    # ======================================================
    # FINANCIAL HEALTH
    # ======================================================

    elif any(word in q for word in [
        "financial health",
        "health score",
        "financial status",
        "how healthy are my finances",
        "how healthy is my financial",
        "health",
        "financial condition"
    ]):

        reply = (
            "❤️ Financial Health Analysis\n\n"
            f"Health Score : {health_score}/100\n"
            f"Status : {health_status}\n\n"
        )

        if health_score >= 80:

            reply += (
                "🌟 Excellent financial health. "
                "Continue maintaining your current "
                "income, savings and spending balance."
            )

        elif health_score >= 60:

            reply += (
                "👍 Your financial health is good. "
                "You can improve it further by increasing "
                "savings and controlling unnecessary expenses."
            )

        else:

            reply += (
                "⚠️ Your financial health needs improvement. "
                "Try reducing expenses and increasing savings."
            )

        chart = {
            "type": "doughnut",
            "title": "Financial Health Score",
            "labels": [
                "Healthy",
                "Remaining"
            ],
            "values": [
                float(health_score),
                float(max(100 - health_score, 0))
            ],
            "label": "Score"
        }

    # ======================================================
    # COMPLETE FINANCIAL SUMMARY
    # ======================================================

    elif any(word in q for word in [
        "complete financial summary",
        "financial summary",
        "overall summary",
        "complete summary",
        "dashboard summary",
        "full financial summary",
        "show everything",
        "my complete finances"
    ]):

        reply = (
            "📊 Complete Financial Summary\n\n"
            f"💰 Income : ₹{total_income:,.2f}\n"
            f"💸 Expenses : ₹{total_expense:,.2f}\n"
            f"💵 Savings : ₹{total_savings:,.2f}\n"
            f"📈 Investment : ₹{total_investment:,.2f}\n"
            f"💼 Portfolio Value : ₹{current_value:,.2f}\n"
            f"💹 ROI : {roi}%\n"
            f"❤️ Health Score : {health_score}/100\n"
            f"📊 Expense Ratio : {expense_percent}%\n"
            f"💵 Savings Rate : {saving_percent}%"
        )

        chart = {
            "type": "bar",
            "title": "Complete Financial Overview",
            "labels": [
                "Income",
                "Expense",
                "Savings",
                "Investment"
            ],
            "values": [
                float(total_income),
                float(total_expense),
                float(max(total_savings, 0)),
                float(total_investment)
            ],
            "label": "Amount"
        }
        # ======================================================
    # BUDGET RECOMMENDATION
    # ======================================================

    elif any(word in q for word in [
        "monthly budget",
        "recommended budget",
        "how much should i keep",
        "how much should i keep for my budget",
        "how much should i keep for monthly budget",
        "budget recommendation",
        "budget summary",
        "budget"
    ]):

        reply = (
            "💰 Recommended Monthly Budget\n\n"
            f"💵 Your Income : ₹{total_income:,.2f}\n\n"
            f"📌 Recommended Budget : "
            f"₹{recommended_budget:,.2f}\n"
            f"💰 Recommended Savings : "
            f"₹{recommended_savings:,.2f}\n"
            f"📈 Recommended Investment : "
            f"₹{recommended_investment:,.2f}\n\n"
            "This recommendation uses a simple "
            "50% budget, 20% savings and 30% "
            "investment allocation."
        )

        chart = {
            "type": "bar",
            "title": "Recommended Income Allocation",
            "labels": [
                "Budget",
                "Savings",
                "Investment"
            ],
            "values": [
                float(recommended_budget),
                float(recommended_savings),
                float(recommended_investment)
            ],
            "label": "Amount"
        }

    # ======================================================
    # HOW MUCH SHOULD I SAVE?
    # ======================================================

    elif any(word in q for word in [
        "how much should i save",
        "how much can i save",
        "save from my income",
        "recommended savings",
        "how much should i save from my income",
        "how much savings should i keep",
        "saving recommendation"
    ]):

        reply = (
            "💵 Recommended Savings Analysis\n\n"
            f"💰 Your Income : ₹{total_income:,.2f}\n"
            f"💵 Current Savings : ₹{total_savings:,.2f}\n"
            f"🎯 Recommended Savings : "
            f"₹{recommended_savings:,.2f}\n\n"
            "A good target is to save around "
            "20% of your income."
        )

        chart = {
            "type": "doughnut",
            "title": "Recommended Savings Allocation",
            "labels": [
                "Savings",
                "Remaining Income"
            ],
            "values": [
                float(recommended_savings),
                float(
                    max(
                        total_income -
                        recommended_savings,
                        0
                    )
                )
            ],
            "label": "Amount"
        }

    # ======================================================
    # HOW MUCH SHOULD I INVEST?
    # ======================================================

    elif any(word in q for word in [
        "how much should i invest",
        "how much can i invest",
        "invest according to my income",
        "recommended investment",
        "how much should i invest according to my income",
        "investment recommendation",
        "investment allocation"
    ]):

        reply = (
            "📈 Recommended Investment\n\n"
            f"💰 Your Income : ₹{total_income:,.2f}\n"
            f"📈 Recommended Investment : "
            f"₹{recommended_investment:,.2f}\n\n"
            "This is a general budgeting guideline "
            "based on 30% of income. It is not "
            "personalized investment advice."
        )

        chart = {
            "type": "doughnut",
            "title": "Recommended Investment Allocation",
            "labels": [
                "Investment",
                "Other Income"
            ],
            "values": [
                float(recommended_investment),
                float(
                    max(
                        total_income -
                        recommended_investment,
                        0
                    )
                )
            ],
            "label": "Amount"
        }

    # ======================================================
    # INVESTMENT SUMMARY
    # ======================================================

    elif any(word in q for word in [
        "total investment",
        "my total investment",
        "show investment",
        "show my investment",
        "investment report",
        "investment summary",
        "my portfolio",
        "portfolio summary",
        "portfolio value",
        "current portfolio value",
        "total portfolio value",
        "investment"
    ]):

        reply = (
            "📈 Investment Portfolio Summary\n\n"
            f"💰 Total Investment : "
            f"₹{total_investment:,.2f}\n"
            f"💼 Current Portfolio Value : "
            f"₹{current_value:,.2f}\n"
            f"💹 Profit/Loss : "
            f"₹{profit_loss:,.2f}\n"
            f"📊 Overall ROI : {roi}%\n\n"
        )

        if profit_loss > 0:

            reply += (
                "✅ Your portfolio is currently "
                "above the invested amount."
            )

        elif profit_loss < 0:

            reply += (
                "⚠️ Your portfolio is currently "
                "below the invested amount."
            )

        else:

            reply += (
                "➖ Your portfolio is currently "
                "at the invested value."
            )

        chart = {
            "type": "bar",
            "title": "Investment Performance",
            "labels": [
                "Invested",
                "Current Value"
            ],
            "values": [
                float(total_investment),
                float(current_value)
            ],
            "label": "Portfolio Value"
        }

    # ======================================================
    # ROI
    # ======================================================

    elif any(word in q for word in [
        "what is my roi",
        "what is overall roi",
        "overall roi",
        "my roi",
        "return on investment",
        "investment return",
        "investment returns",
        "returns",
        "roi"
    ]):

        reply = (
            "💹 Investment Return Analysis\n\n"
            f"📊 Overall ROI : {roi}%\n"
            f"💰 Invested Amount : "
            f"₹{total_investment:,.2f}\n"
            f"💼 Current Value : "
            f"₹{current_value:,.2f}\n"
            f"💵 Profit/Loss : "
            f"₹{profit_loss:,.2f}\n\n"
        )

        if roi > 15:

            reply += (
                "📈 Your portfolio is showing "
                "strong positive returns."
            )

        elif roi > 0:

            reply += (
                "📊 Your portfolio is generating "
                "positive returns."
            )

        elif roi == 0:

            reply += (
                "➖ Your portfolio is currently "
                "at the invested value."
            )

        else:

            reply += (
                "📉 Your portfolio is currently "
                "showing a negative return."
            )

        chart = {
            "type": "bar",
            "title": "Investment Return",
            "labels": [
                "Investment",
                "Current Value"
            ],
            "values": [
                float(total_investment),
                float(current_value)
            ],
            "label": "Value"
        }

    # ======================================================
    # BEST INVESTMENT
    # ======================================================

    elif any(word in q for word in [
        "best investment",
        "which is my best investment",
        "highest roi",
        "top investment",
        "best performing investment",
        "performing best",
        "which investment is performing best"
    ]):

        investments = Investment.query.all()

        if investments:

            best = max(
                investments,
                key=lambda x: (
                    (
                        (
                            x.current_value -
                            x.invested_amount
                        )
                        /
                        x.invested_amount
                    )
                    if x.invested_amount
                    else 0
                )
            )

            best_roi = (
                (
                    best.current_value -
                    best.invested_amount
                )
                /
                best.invested_amount
                * 100
            ) if best.invested_amount else 0

            reply = (
                "🏆 Best Performing Investment\n\n"
                f"📌 Investment : "
                f"{best.investment_name}\n"
                f"💰 Invested Amount : "
                f"₹{best.invested_amount:,.2f}\n"
                f"💼 Current Value : "
                f"₹{best.current_value:,.2f}\n"
                f"📈 ROI : {best_roi:.2f}%"
            )

            chart = {
                "type": "bar",
                "title": "Best Investment Performance",
                "labels": [
                    "Invested",
                    "Current Value"
                ],
                "values": [
                    float(best.invested_amount),
                    float(best.current_value)
                ],
                "label": "Value"
            }

        else:

            reply = (
                "No investment records were found."
            )

    # ======================================================
    # WORST / POOR INVESTMENT
    # ======================================================

    elif any(word in q for word in [
        "worst investment",
        "lowest roi",
        "poor investment",
        "poorly performing",
        "performing poorly",
        "which investment is performing poorly",
        "loss investment",
        "worst performing investment"
    ]):

        investments = Investment.query.all()

        if investments:

            worst = min(
                investments,
                key=lambda x: (
                    (
                        (
                            x.current_value -
                            x.invested_amount
                        )
                        /
                        x.invested_amount
                    )
                    if x.invested_amount
                    else 0
                )
            )

            worst_roi = (
                (
                    worst.current_value -
                    worst.invested_amount
                )
                /
                worst.invested_amount
                * 100
            ) if worst.invested_amount else 0

            reply = (
                "📉 Poorly Performing Investment\n\n"
                f"📌 Investment : "
                f"{worst.investment_name}\n"
                f"💰 Invested Amount : "
                f"₹{worst.invested_amount:,.2f}\n"
                f"💼 Current Value : "
                f"₹{worst.current_value:,.2f}\n"
                f"📉 ROI : {worst_roi:.2f}%"
            )

            chart = {
                "type": "bar",
                "title": "Lowest Performing Investment",
                "labels": [
                    "Invested",
                    "Current Value"
                ],
                "values": [
                    float(worst.invested_amount),
                    float(worst.current_value)
                ],
                "label": "Value"
            }

        else:

            reply = (
                "No investment records were found."
            )
    # ======================================================
    # FINANCIAL ADVICE
    # ======================================================

    elif any(word in q for word in [
        "financial advice",
        "give me advice",
        "advice",
        "tips",
        "suggestion",
        "suggestions",
        "recommendation",
        "recommendations",
        "how can i improve",
        "how can i improve my financial health",
        "improve financial health"
    ]):

        advice = []

        if total_expense > total_income:

            advice.append(
                "🔴 Reduce unnecessary expenses because "
                "your expenses are higher than your income."
            )

        else:

            advice.append(
                "🟢 Your expenses are currently within "
                "your income."
            )

        if saving_percent < 20:

            advice.append(
                "💵 Try to save at least 20% of your income."
            )

        else:

            advice.append(
                "✅ Your savings rate is healthy."
            )

        if roi < 10:

            advice.append(
                "📈 Review your investment portfolio "
                "regularly."
            )

        else:

            advice.append(
                "📊 Your investment returns are performing well."
            )

        if health_score < 60:

            advice.append(
                "❤️ Focus on improving your income-to-expense "
                "balance."
            )

        else:

            advice.append(
                "🌟 Maintain your current financial discipline."
            )

        reply = (
            "💡 Personalized Financial Advice\n\n"
            + "\n\n".join(advice)
        )

        chart = {
            "type": "bar",
            "title": "Financial Position",
            "labels": [
                "Income",
                "Expense",
                "Savings"
            ],
            "values": [
                float(total_income),
                float(total_expense),
                float(max(total_savings, 0))
            ],
            "label": "Amount"
        }

    # ======================================================
    # FINANCIAL ALERTS
    # ======================================================

    elif any(word in q for word in [
        "financial alerts",
        "do i have any financial alerts",
        "do i have alerts",
        "alerts",
        "alert",
        "notification",
        "notifications",
        "warning",
        "financial warning"
    ]):

        if alerts:

            reply = (
                "🚨 Financial Alerts\n\n"
                + "\n".join(
                    "• " + alert
                    for alert in alerts
                )
            )

        else:

            reply = (
                "✅ You currently have no financial alerts.\n\n"
                "Your financial records do not show "
                "any major warning conditions."
            )

    # ======================================================
    # FINANCIAL GOALS
    # ======================================================

    elif any(word in q for word in [
        "financial goal",
        "financial goals",
        "goal",
        "goals",
        "goal progress",
        "how can i reach my goals"
    ]):

        reply = (
            "🎯 Financial Goal Suggestions\n\n"
            "1. 💵 Save at least 20% of your income.\n"
            "2. 💸 Keep expenses below your income.\n"
            "3. 📈 Invest regularly according to your capacity.\n"
            "4. 🏦 Maintain an emergency fund.\n"
            "5. 📊 Review your budget every month.\n"
            "6. ❤️ Try to improve your financial health score."
        )

    # ======================================================
    # DEFAULT RESPONSE
    # ======================================================

    else:

        reply = (
            "🤖 I understood your question, but I need "
            "a little more information to give a specific "
            "financial answer.\n\n"
            "Try asking about:\n\n"
            "💰 Income\n"
            "💸 Expenses\n"
            "💵 Savings\n"
            "📊 Financial Health\n"
            "💰 Budget\n"
            "📈 Investments\n"
            "💹 ROI\n"
            "🏆 Best Investment\n"
            "📉 Poor Investment\n"
            "🚨 Financial Alerts\n"
            "💡 Financial Advice\n\n"
            "Example:\n"
            "\"What is my total income?\"\n"
            "\"Am I spending more than I earn?\"\n"
            "\"Show my investment report.\""
        )

    # ======================================================
    # SAVE CHAT HISTORY
    # ======================================================

    history = ChatHistory(
        question=question,
        answer=reply,
        date=datetime.now().strftime(
            "%d-%m-%Y %H:%M"
        )
    )

    db.session.add(history)

    db.session.commit()

    # ======================================================
    # FINAL JSON RESPONSE
    # ======================================================

    return jsonify({

        "greeting": greeting,

        "reply": reply,

        "chart": chart,

        "tips": tips,

        "alerts": alerts,

        "total_income": float(
            total_income
        ),

        "total_expense": float(
            total_expense
        ),

        "total_savings": float(
            total_savings
        ),

        "total_investment": float(
            total_investment
        ),

        "current_value": float(
            current_value
        ),

        "health_score": health_score,

        "health_status": health_status,

        "saving_percent": saving_percent,

        "expense_percent": expense_percent,

        "profit_loss": float(
            profit_loss
        ),

        "roi": roi,

        "ideal_budget": float(
            recommended_budget
        ),

        "ideal_savings": float(
            recommended_savings
        ),

        "ideal_investment": float(
            recommended_investment
        )

    })


@app.route("/jarvis")
def jarvis():

    return render_template("jarvis.html")


# =========================================================
# CHAT HISTORY
# =========================================================

@app.route("/chat_history")
def chat_history():

    chats = ChatHistory.query.order_by(
        ChatHistory.id.desc()
    ).all()

    return render_template(
        "chat_history.html",
        chats=chats
    )


# =========================================================
# CLEAR CHAT
# =========================================================

@app.route("/clear_chat")
def clear_chat():

    ChatHistory.query.delete()

    db.session.commit()

    return redirect("/jarvis")


# =========================================================
# DOWNLOAD CHAT TXT
# =========================================================

@app.route("/download_chat")
def download_chat():

    chats = ChatHistory.query.order_by(
        ChatHistory.id.asc()
    ).all()

    file_name = "Jarvis_Chat_History.txt"

    with open(
        file_name,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(
            "JARVIS AI FINANCIAL ASSISTANT\n"
        )

        f.write(
            "=" * 50 + "\n\n"
        )

        for chat in chats:

            f.write(
                f"Question: {chat.question}\n"
            )

            f.write(
                f"Answer: {chat.answer}\n"
            )

            f.write(
                f"Date: {chat.date}\n"
            )

            f.write(
                "-" * 50 + "\n\n"
            )

    return send_file(
        file_name,
        as_attachment=True
    )


# =========================================================
# DOWNLOAD CHAT PDF
# =========================================================
@app.route("/download_chat_pdf")
def download_chat_pdf():

    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.enums import TA_CENTER
    from io import BytesIO
    # Create PDF in memory
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()

    title_style = styles["Title"]
    title_style.alignment = TA_CENTER

    story = []

    story.append(
        Paragraph("JARVIS AI - Chat History", title_style)
    )

    story.append(Spacer(1, 20))

    # Get chat history
    chats = session.get("chat_history", [])

    if not chats:

        story.append(
            Paragraph(
                "No chat history available.",
                styles["Normal"]
            )
        )

    else:

        for chat in chats:

            question = chat.get("question", "")
            answer = chat.get("answer", "")

            story.append(
                Paragraph(
                    "<b>You:</b> " + str(question),
                    styles["Normal"]
                )
            )

            story.append(Spacer(1, 8))

            story.append(
                Paragraph(
                    "<b>Jarvis:</b> " + str(answer),
                    styles["Normal"]
                )
            )

            story.append(Spacer(1, 15))

    doc.build(story)

    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name="jarvis_chat_history.pdf",
        mimetype="application/pdf"
    )

# ==========================================================
# JARVIS FINANCIAL OVERVIEW DATA
# ==========================================================

@app.route("/jarvis_financial_overview")
def jarvis_financial_overview():

    total_income = db.session.query(
        db.func.sum(Income.amount)
    ).scalar() or 0

    total_expense = db.session.query(
        db.func.sum(Expense.amount)
    ).scalar() or 0

    total_savings = total_income - total_expense

    total_investment = db.session.query(
        db.func.sum(Investment.invested_amount)
    ).scalar() or 0

    current_value = db.session.query(
        db.func.sum(Investment.current_value)
    ).scalar() or 0

    if total_investment > 0:
        profit_loss = current_value - total_investment

        roi = (
            profit_loss / total_investment
        ) * 100

    else:
        profit_loss = 0
        roi = 0

    if total_income > 0:

        health_score = round(
            (
                total_income /
                (total_income + total_expense)
            ) * 100
        )

    else:

        health_score = 0

    return jsonify({

        "income": float(total_income),

        "expense": float(total_expense),

        "savings": float(total_savings),

        "investment": float(total_investment),

        "current_value": float(current_value),

        "profit_loss": float(profit_loss),

        "roi": round(float(roi), 2),

        "health_score": health_score

    })

if __name__ == "__main__":
    app.run(debug=True)