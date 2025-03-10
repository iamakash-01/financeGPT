import os
import json
from datetime import datetime
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.groq import Groq

# load the groq api key
load_dotenv()
groq_api_key = os.getenv('GROQ_API_KEY')

# expense, bills and debts file
expense_file = 'expenses.json'
budget_file = 'budget.json'
bills_file = 'bills.json'
debt_file = 'debt.json'

# ----------------------------------------load files------------------------------------------------
def load_data(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            return json.load(file)
    return []

def save_data(data, file_path):
    try:
        with open(file_path, "w") as file:
            json.dump(data, file, indent = 4)
    except IOError :
        print(f'Error saving the file {file_path}. Please try again.')

# ----------------------------------------Expense functions-------------------------------------------
def add_expense(amount, category, description = ""):
    expenses = load_data(expense_file)
    expense = {
        "amount": float(amount),
        "category": category,
        "description": description,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    expenses.append(expense)
    save_data(expenses, expense_file)
    return f"\nAdded: ${amount} in {category} - {description}"

def show_expenses():
    expenses = load_data(expense_file)
    if not expenses:
        return "No expenses recorded yet."

    total = 0
    response = "\n Expense History: \n" + "-" * 40 + "\n"
    for exp in expenses:
        response += f"{exp['date']} | ${exp['amount']} | {exp['category']} | {exp['description']}\n"
        total += exp["amount"]
    response += "-" * 40 + f"\n Total Spent: ${total}"
    return response

def show_category_summary():
    expenses = load_data(expense_file)
    category_totals = {}

    for exp in expenses:
        category_totals[exp["category"]] = category_totals.get(exp["category"], 0) + exp["amount"]

    if not category_totals:
        return "No expenses recorded yet."

    response = "\n Category-wise Breakdown: \n"
    for category, total in category_totals.items():
        response += f" ~ {category}: ${total}\n"
    
    return response

# --------------------------------------Budget function------------------------------------------------
def set_budget(amount):
    save_data({'monthly budget': float(amount)}, budget_file)
    print(f'Budget set to ${amount: .2f} per month')

def get_budget():
    budget_data = load_data(budget_file)
    return budget_data.get("monthly_budget", 0) if budget_data else 0

def check_budget():
    budget = get_budget()
    if budget == 0:
        return "No budget set. Use 'Set Budget' option."

    expenses = load_data(expense_file)
    total_spent = sum(exp["amount"] for exp in expenses)
    
    response = f"\nBudget Overview:\nBudget: ${budget:.2f}\nSpent: ${total_spent:.2f}\n"
    if total_spent > budget:
        response += "Warning: You have exceeded your budget!"
    else:
        remaining = budget - total_spent
        response += f"You have ${remaining:.2f} left this month."
    
    return response
# -----------------------------------------Spending fuctions------------------------------------------
def spending_insights():
    expenses = load_data(expense_file)
    if not expenses:
        return "No expenses recorded yet."

    total_spent = sum(exp["amount"] for exp in expenses)
    category_totals = {}
    for exp in expenses:
        category_totals[exp["category"]] = category_totals.get(exp["category"], 0) + exp["amount"]

    finance_agent = Agent(
        model=Groq(id="llama-3.3-70b-versatile"),
        description="You are an AI finance assistant analyzing spending patterns.",
        markdown=True
    )

    prompt = f"""
    Analyze user spending data:
    - Total spent: ${total_spent:.2f}
    - Category breakdown: {category_totals}
    Provide money-saving advice.
    """

    print("\nAI Spending Insights:\n")
    finance_agent.print_response(prompt, stream=True)

def detect_spending_pattern():
    expenses = load_data(expense_file)
    if len(expenses) < 5:
        return "Not enough data to detect spending patterns."

    last_expenses = expenses[-5:]
    total_last_5 = sum(exp["amount"] for exp in last_expenses)
    avg_spending = total_last_5 / 5
    threshold = avg_spending * 1.5

    last_expense = expenses[-1]
    is_unusual = last_expense["amount"] > threshold

    # AI-powered analysis
    finance_agent = Agent(
        model=Groq(id="llama-3.3-70b-versatile"),
        description="You analyze spending patterns and detect unusual trends.",
        markdown=True
    )

    prompt = f"""
    The user has made the following recent expenses:
    {json.dumps(last_expenses, indent=4)}
    
    - Average recent spending: ${avg_spending:.2f}
    - Last recorded expense: ${last_expense['amount']:.2f}
    
    Detect if this is unusual compared to their past spending trends.  
    If it's unusually high, provide a **friendly warning**.  
    If it's normal, offer **budgeting tips** based on their spending.  
    """

    print("\nAI-Powered Spending Pattern Analysis:\n")
    finance_agent.print_response(prompt, stream=True)

# ------------------------------------------Main loop--------------------------------------------------
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
        print(spending_insights())

    elif user_input == '4':
        print(detect_spending_pattern())

    else:
        print('Invalid Choice. Please try again.')