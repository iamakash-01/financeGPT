import os
import json
from datetime import datetime
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.groq import Groq
from agno.tools.yfinance import YFinanceTools

# load the groq api key
load_dotenv()
groq_api_key = os.getenv('GROQ_API_KEY')

# expense file
expense_file = 'expenses.json'
budget_file = 'budget.json'

# functioons for expense tracking
def load_expenses():
    if os.path.exists(expense_file):
        with open(expense_file, "r") as file:
            return json.load(file)
    return []

def save_expenses(expenses):
    try:
        with open(expense_file, "w") as file:
            json.dump(expenses, file, indent=4)
    except IOError :
        print('Error saving the file. Please try again.')

def add_expense(amount, category, description=""):
    """Add a new expense."""
    expenses = load_expenses()
    expense = {
        "amount": float(amount),
        "category": category,
        "description": description,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    expenses.append(expense)
    save_expenses(expenses)
    return f"\n Added: ${amount} in {category} - {description}"

def show_expenses():
    """Display all expenses."""
    expenses = load_expenses()
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
    """Show expenses by category."""
    expenses = load_expenses()
    category_totals = {}

    for exp in expenses:
        category_totals[exp["category"]] = category_totals.get(exp["category"], 0) + exp["amount"]

    if not category_totals:
        return "No expenses recorded yet."

    response = "\n Category-wise Breakdown: \n"
    for category, total in category_totals.items():
        response += f" ~ {category}: ${total}\n"
    
    return response

# Budget function
def set_budget(amount):
    """Set a monthly budget."""
    budget_data = {"monthly_budget": float(amount)}
    with open(budget_file, "w") as file:
        json.dump(budget_data, file)
    print(f"Budget set to ${amount:.2f} per month.")

def get_budget():
    """Get the saved budget amount."""
    if os.path.exists(budget_file):
        try:
            with open(budget_file, "r") as file:
                budget_data = json.load(file)
                return budget_data.get("monthly_budget", 0)
        except (json.JSONDecodeError, IOError):
            return 0
    return 0
def check_budget():
    """Check if total expenses exceed the budget."""
    budget = get_budget()
    if budget == 0:
        return "No budget set. Use the 'Set Budget' option."

    expenses = load_expenses()
    total_spent = sum(exp["amount"] for exp in expenses)
    
    response = f"\n Budget Overview: \n"
    response += f" Budget: ${budget:.2f} \n"
    response += f" Spent: ${total_spent:.2f} \n"

    if total_spent > budget:
        response += " Warning: You have exceeded your budget! "
    else:
        remaining = budget - total_spent
        response += f" You have ${remaining:.2f} left this month."
    
    return response

while True:
    # some basic prompts
    print('Welcome to the FinanceGPT \n')
    print('What do you want to do?')
    print('1. Personal Finance Assistance')
    print('2. Expense Tracking')
    print('3. Exit')

    # user choice
    try:
        user_input = input('Enter your choice please or type(exit) to exit : ').strip().lower()
    except Exception as e:
        print('Invalid input, please enter any of the choices above')
        exit(1)

    if user_input == 'exit' or user_input == '3':
        print('Thank you for using the FinanceGPT...Have a nice day.')
        break

    try:
        user_choice = int(user_input)
    except ValueError:
        print('Invalid input, please enter a number.')
        continue

    if user_choice == 4:
        print('Thank you for using the Magical Financial Assistant...Have a nice day.')
        break

    if user_choice == 1:
        user_input = input('Enter your finance related question please or type(exit) : ').strip().lower()
        if user_input.lower() == 'exit':
            break
        
        finance_agent = Agent(
            model = Groq(id = "llama-3.3-70b-versatile"),
            description = 'You are a finance agent',
            markdown = True
    )
        finance_agent.print_response(user_input, stream = True)

    elif user_choice == 2:
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
    else:
        print('Invalid choice, please enter a valid choice')