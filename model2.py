import os
import sqlite3
from datetime import datetime
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.groq import Groq

# load the groq api key
load_dotenv()
groq_api_key = os.getenv('GROQ_API_KEY')

# connect to database
db_file = 'finance.db'
def connect_db():
    return sqlite3.connect(db_file)

#----------------------------------------Database Operations----------------------------------------------
def create_tables():
    conn = connect_db()
    cursor = conn.cursor()
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS expenses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    amount REAL,
                    category TEXT,
                    description TEXT,
                    date TEXT)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS budget (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    monthly_budget REAL)''')

    conn.commit()
    conn.close()

# ----------------------------------------Expense functions-------------------------------------------
def add_expense(amount, category, description = ""):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("INSERT INTO expenses (amount, category, description, date) VALUES (?, ?, ?, ?)",
                   (amount, category, description, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

    conn.commit()
    conn.close()
    return f"\nAdded: ${amount} in {category} - {description}"

def show_expenses():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM expenses")
    expenses = cursor.fetchall()
    conn.close()

    if not expenses:
        return "No expenses recorded yet."

    response = "\nExpense History:\n" + "-" * 40 + "\n"
    total = 0
    for exp in expenses:
        response += f"{exp[4]} | ${exp[1]} | {exp[2]} | {exp[3]}\n"
        total += exp[1]

    response += "-" * 40 + f"\nTotal Spent: ${total}"
    return response
def show_category_summary():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT category, SUM(amount) FROM expenses GROUP BY category")
    category_totals = cursor.fetchall()

    conn.close()

    if not category_totals:
        return "No expenses recorded yet."

    response = "\nCategory-wise Breakdown:\n"
    for category, total in category_totals:
        response += f"~ {category}: ${total:.2f}\n"

    return response

# --------------------------------------Budget function------------------------------------------------
def set_budget(amount):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM budget")  # Ensure only one budget exists
    cursor.execute("INSERT INTO budget (monthly_budget) VALUES (?)", (amount,))
    
    conn.commit()
    conn.close()
    print(f"Budget set to ${amount:.2f} per month.")
def get_budget():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT monthly_budget FROM budget")
    result = cursor.fetchone()

    conn.close()

    return result[0] if result else 0

def check_budget():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT monthly_budget FROM budget")
    result = cursor.fetchone()

    if not result:
        return "No budget set. Use the 'Set Budget' option."

    budget = result[0]
    
    cursor.execute("SELECT SUM(amount) FROM expenses")
    total_spent = cursor.fetchone()[0] or 0

    conn.close()

    response = f"\nBudget Overview:\nBudget: ${budget:.2f}\nSpent: ${total_spent:.2f}\n"

    if total_spent > budget:
        response += "Warning: You have exceeded your budget!"
    else:
        remaining = budget - total_spent
        response += f"You have ${remaining:.2f} left this month."

    return response

# -----------------------------------------Spending fuctions------------------------------------------
def spending_insights():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT category, SUM(amount) FROM expenses GROUP BY category")
    category_totals = cursor.fetchall()

    cursor.execute("SELECT SUM(amount) FROM expenses")
    total_spent = cursor.fetchone()[0] or 0

    conn.close()

    if not category_totals:
        return "No expenses recorded yet."

    finance_agent = Agent(
        model=Groq(id="llama-3.3-70b-versatile"),
        description="You analyze spending data and provide financial advice.",
        markdown=True
    )

    prompt = f"""
    User's total spending: ${total_spent:.2f}
    Category breakdown: {dict(category_totals)}

    Suggest money-saving strategies and budget improvements.
    """

    print("\n AI-Powered Spending Insights:\n")
    finance_agent.print_response(prompt, stream=True)

def detect_spending_pattern():
    conn = connect_db()
    cursor = conn.cursor()

    # Get total spending for the last 7 days
    cursor.execute("""
        SELECT SUM(amount) FROM expenses
        WHERE date >= date('now', '-7 days')
    """)
    last_week_spending = cursor.fetchone()[0] or 0

    # Get total spending for the previous 7 days (8-14 days ago)
    cursor.execute("""
        SELECT SUM(amount) FROM expenses
        WHERE date >= date('now', '-14 days') AND date < date('now', '-7 days')
    """)
    prev_week_spending = cursor.fetchone()[0] or 0

    conn.close()

    # Check if there’s enough data
    if last_week_spending == 0 and prev_week_spending == 0:
        return "Not enough data to detect weekly spending patterns."

    # Calculate the percentage change in spending
    if prev_week_spending == 0:
        change_percent = 100  # If no previous spending, assume full increase
    else:
        change_percent = ((last_week_spending - prev_week_spending) / prev_week_spending) * 100

    # AI-powered spending insights
    finance_agent = Agent(
        model=Groq(id="llama-3.3-70b-versatile"),
        description="You analyze weekly spending patterns and detect trends.",
        markdown=True
    )

    prompt = f"""
    User's weekly spending data:
    - Last 7 days: ${last_week_spending:.2f}
    - Previous 7 days: ${prev_week_spending:.2f}
    - Percentage change: {change_percent:.2f}%

    Analyze whether the user is overspending or saving compared to the previous week.
    Provide personalized advice to improve financial habits.
    """

    print("\nAI-Powered Weekly Spending Pattern Analysis:\n")
    finance_agent.print_response(prompt, stream=True)

# ------------------------------------------Main loop--------------------------------------------------
create_tables()
while True:
    # some basic prompts
    print('Welcome to the FinanceGPT \n')
    print('What do you want to do?')
    print('1. Personal Finance Assistance')
    print('2. Expense Tracking and Budget Analysis')
    print('3. AI powered Spending Insights')
    print('4. Detect Spending Patterns')
    print('5. Exit')

    # user choice
    try:
        user_input = input('Enter your choice please or type(exit) to exit : ').strip().lower()
    except Exception as e:
        print('Invalid input, please enter any of the choices above')
        exit(1)

    if user_input == 'exit' or user_input == '5':
        print('Thank you for using the FinanceGPT...Have a nice day.')
        break

    try:
        user_choice = int(user_input)
    except ValueError:
        print('Invalid input, please enter a number.')
        continue

    if user_choice == 5:
        print('Thank you for using the FinanceGPT...Have a nice day.')
        break

    if user_choice == 1: # financial agent
        user_input = input('Enter your finance related question please or type(exit) : ').strip().lower()
        if user_input.lower() == 'exit':
            break
        
        finance_agent = Agent(
            model = Groq(id = "llama-3.3-70b-versatile"),
            description = 'You are a finance agent',
            markdown = True
    )
        finance_agent.print_response(user_input, stream = True)

    elif user_choice == 2: # expense tracking
        while True:
            print("\n-------Expense Tracker Menu-------")
            print("1. Add Expense")
            print("2. Show Expenses")
            print("3. Show Summary")
            print('4. Set Monthly Budget')
            print('5. Check Budget status')
            print("6. Exit to Main menu")

            expense_choice = input("Enter your choice (1-6) or type(exit): ").strip().lower()

            if expense_choice == 'exit' or expense_choice == '6':
                break

            if expense_choice == "1":
                try:
                    amount = float(input("Enter amount: "))
                    category = input("Enter category (Food, Travel, Bills, etc.): ")
                    description = input("Enter description (optional): ")
                    print(add_expense(amount, category, description))
                except ValueError:
                    print("Invalid amount. Please enter a number.")

            elif expense_choice == "2":
                print(show_expenses())

            elif expense_choice == "3":
                print(show_category_summary())

            elif expense_choice == "4":
                try:
                    budget_amount = float(input("Enter your monthly budget: "))
                    set_budget(budget_amount)
                except ValueError:
                    print("Invalid amount. Please enter a valid number.")

            elif expense_choice == "5":
                print(check_budget())
            
            else:
                print("Invalid choice. Please enter a number between 1 and 6.")
    elif user_input == '3':
        spending_insights()

    elif user_input == '4':
        print(detect_spending_pattern())

    else:
        print('Invalid Choice. Please try again.')