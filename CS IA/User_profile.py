import profile
import sqlite3


def create_database():
    connect = sqlite3.connect('user_profile.db')
    cursor = connect.cursor()

    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_profile_table (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        spouse_status TEXT,
        parental_status TEXT,
        age INTEGER,
        retirement_age INTEGER,
        relationship TEXT,
        main_profile_id INTEGER,
        annual_income INTEGER,
        annual_expenses INTEGER,
        current_assets INTEGER,
        interested_sectors TEXT,
        risk_tolerance INTEGER,
        money_by_retirement INTEGER,
        interested_dividend INTEGER,
        market_cap_preference INTEGER,
        percentage_disposable_income_investable REAL
    )
    ''')

    connect.commit()
    return connect, cursor

# General Information
def user_input():
    while True:
        try:
            name = str(input("input name "))
            break
        except ValueError:
            print("Invalid input. Please enter valid values.")
            return
        
    while True:
        try:
            spouse_status = str(input("input status: single, married, divorced "))
            if spouse_status not in ["single", "married", "divorced"]:
                raise ValueError("Invalid status. Please enter one of the following: single, married, divorced")
            break
        except ValueError:
            print(f"Invalid input. Please enter valid values.")
            return
        
    while True:
        try:
            parental_status = str(input("input status: parent, non-parent "))
            if parental_status not in ["parent", "non-parent"]:
                raise ValueError("Invalid status. Please enter one of the following: parent, non-parent")
            break
        except ValueError:
            print(f"Invalid input. Please enter valid values.")
            return
        
    while True:
        try:
            age = int(input("input age "))
            break
        except ValueError:
            print("Invalid input. Please enter valid values.")
            return

    while True:
        try:
            retirement_age = int(input("input retirement age "))
            break
        except ValueError:
            print("Invalid input. Please enter valid values.")
            return
         
# Personal Finances 
    while True:
        try:
            annual_income = int(input("input annual income "))
            break
        except ValueError:
            print("Invalid input. Please enter valid values.")
            return
        
    while True:
        try:
            annual_expenses = int(input("input annual expenses "))
            break
        except ValueError:
            print("Invalid input. Please enter valid values.")
            return

    while True:
        try:
            current_assets = int(input("input current assets "))
            break
        except ValueError:
            print("Invalid input. Please enter valid values.")
            return

# Investment Preferences
    while True:
        try:
            interested_sectors = str(input("input interested sectors "))
            break
        except ValueError:
            print("Invalid input. Please enter valid values.")

            return

    while True:
        try:
            risk_tolerance = int(input("input risk tolerance 1-3, 1 being low and 3 being high"))
            if risk_tolerance not in range(1, 4):
                raise ValueError("Invalid risk tolerance value. Please enter a number between 1 and 3 ")
            break
        except ValueError as e:
            print(f"Invalid input. {e}")
            return
        except ValueError as e:
            print(f"Invalid input. {e}")
            return
        
    while True:
        try:
            percentage_disposable_income_investable = float(input("input percentage of disposable income to invest "))
            if not (0 <= percentage_disposable_income_investable <= 100):
                raise ValueError("Invalid percentage. Please enter a value between 0 and 100.")
            break
        except ValueError as e:
            print(f"Invalid input. {e}")
            return

# Financial Goals
    while True:
        try:
            money_by_retirement = int(input("input how much money you want by retirement "))
            break
        except ValueError:
            print("Invalid input. Please enter valid values.")
            return

    while True:
        try: 
            interested_dividend = int(input("input your interested percentage of dividend "))
            break
        except ValueError:
                print("Invalid input. Please enter valid values.")
                return

    while True:
        try: 
            market_cap_preference = int(input("input your market cap preference, 1 being large, 2 medium, 3 small: "))
            break
        except ValueError:
            print("Invalid input. Please enter valid values.")
            return
        
        
    return (
        name, age, retirement_age, annual_income,
        annual_expenses, current_assets, interested_sectors,
        risk_tolerance, money_by_retirement,
        spouse_status, parental_status, interested_dividend, market_cap_preference, percentage_disposable_income_investable
    )

def create_user_profile(
    cursor, connect, relationship, main_profile_id,
    name, age, retirement_age, annual_income,
    annual_expenses, current_assets, interested_sectors,
    risk_tolerance, money_by_retirement,
    spouse_status, parental_status, interested_dividend, market_cap_preference, percentage_disposable_income_investable
):
    cursor.execute("""
    INSERT INTO user_profile_table (
        name, spouse_status, parental_status, age, retirement_age,
        relationship, main_profile_id,
        annual_income, annual_expenses, current_assets,
        interested_sectors, risk_tolerance, money_by_retirement, interested_dividend, market_cap_preference, percentage_disposable_income_investable
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", (
    name, spouse_status, parental_status, age, retirement_age,
    relationship, main_profile_id,
    annual_income, annual_expenses, current_assets,
    interested_sectors, risk_tolerance, money_by_retirement, interested_dividend, market_cap_preference, percentage_disposable_income_investable
))

    connect.commit()

    cursor.execute("SELECT * FROM user_profile_table")
    profiles = cursor.fetchall()

    for profile in profiles:
        print(profile)

# Risk Algo
def risk_algorithm(risk_tolerance):
    if risk_tolerance == 1:
        return "Low Risk"
    elif risk_tolerance == 2:
        return "Medium Risk"
    elif risk_tolerance == 3:
        return "High Risk"

# Calulate algo
def tax(annual_income):
    if annual_income <= 150000:
        return 0

    elif annual_income <= 300000:
        return (annual_income - 150000) * 0.05

    elif annual_income <= 500000:
        return 7500 + (annual_income - 300000) * 0.10

    elif annual_income <= 750000:
        return 27500 + (annual_income - 500000) * 0.15

    elif annual_income <= 1000000:
        return 65000 + (annual_income - 750000) * 0.20

    elif annual_income <= 2000000:
        return 115000 + (annual_income - 1000000) * 0.25

    elif annual_income <= 5000000:
        return 365000 + (annual_income - 2000000) * 0.30
    else:
        return 1265000 + (annual_income - 5000000) * 0.35

def inflation_adjustment(money_by_retirement, age, retirement_age, inflation_rate):
    year_till_retirement = retirement_age - age
    real_goal = money_by_retirement * ((1 + inflation_rate) ** year_till_retirement)
    return real_goal

def required_monthly_savings(adjusted_goal, current_assets, age, retirement_age):
    years_till_retirement = retirement_age - age
    months_till_retirement = years_till_retirement * 12

    remaining_amount = adjusted_goal - current_assets

    if remaining_amount <= 0:
        return 0, remaining_amount, months_till_retirement

    monthly_savings_needed = remaining_amount / months_till_retirement

    return monthly_savings_needed, remaining_amount, months_till_retirement

def progress(annual_income, annual_expenses, required_monthly_savings):
    annual_tax = tax(annual_income)
    income_after_tax = annual_income - annual_tax
    annual_savings = income_after_tax - annual_expenses
    monthly_savings = annual_savings / 12
    progress_amount = monthly_savings - required_monthly_savings

    if progress_amount < 0:
        print(f"You are below the required savings per month by {abs(progress_amount)}")
    elif progress_amount > 0:
        print(f"You are above the required savings per month by {progress_amount}")
    else:
        print("You are exactly on track with the required savings per month.")

def get_user_profile(cursor, user_id):
    cursor.execute("SELECT * FROM user_profile_table WHERE id = ?", (user_id,))
    profile = cursor.fetchone()
    return profile

def get_linked_profiles(cursor, main_profile_id):
    cursor.execute(
        "SELECT * FROM user_profile_table WHERE main_profile_id = ?",
        (main_profile_id,)
    )
    return cursor.fetchall()

def add_linked_profile(cursor, connect, main_profile_id):
    main_profile = get_user_profile(cursor, main_profile_id)

    if main_profile is None:
        print("main profile not found.")
        return

    relationship = input(
        "Enter relationship: spouse, child, or family: "
    ).lower()

    valid_relationships = ["spouse", "child", "family"]

    if relationship not in valid_relationships:
        print("Relationship is invalid.")
        return

    profile_data = user_input()

    if profile_data is None:
        return

    create_user_profile(
        cursor,
        connect,
        relationship,
        main_profile_id,
        *profile_data
    )

    print("linked profile created")

def create_household_profile(main_profile, linked_profiles):
    main_risk = main_profile[12]
    household_income = main_profile[8]
    household_expenses = main_profile[9]
    household_assets = main_profile[10]
    members = 1

    if linked_profiles:
        linked_risk_total = sum(linked_profile[12] for linked_profile in linked_profiles)
        linked_risk_average = linked_risk_total / len(linked_profiles)
        household_risk = round((main_risk * 0.7) + (linked_risk_average * 0.3))
    else:
        household_risk = main_risk

    for linked_profile in linked_profiles:
        household_income += linked_profile[8]
        household_expenses += linked_profile[9]
        household_assets += linked_profile[10]
        members += 1    

    return {
        "members": members,
        "annual_income": household_income,
        "annual_expenses": household_expenses,
        "current_assets": household_assets,
        "age": main_profile[4],
        "retirement_age": main_profile[5],
        "interested_sector": main_profile[11],
        "risk_tolerance": household_risk,
        "money_by_retirement": main_profile[13],
        "interested_dividend": main_profile[14],
        "market_cap_preference": main_profile[15],
        "percentage_disposable_income_investable": main_profile[16]
    }

def main():
    connect, cursor = create_database()

    create_new = input(
        "Do you want to create a new main profile? yes or no: "
    ).lower()

    if create_new == "yes":
        profile_data = user_input()

        if profile_data is not None:
            create_user_profile(
                cursor,
                connect,
                "Main User",
                None,
                *profile_data
            )

    user_id = int(input("Enter profile ID: "))

    profile = get_user_profile(cursor, user_id)

    if profile is None:
        print("No profile found with that ID.")
    else:
        add_linked = input("Do you want to add a linked profile? yes or no: ")

        if add_linked == "yes":
            add_linked_profile(cursor, connect, user_id)
        
        linked_profiles = get_linked_profiles(cursor, user_id)
        household_profile = create_household_profile(profile, linked_profiles)

        print("Household profile:", household_profile)

        name = profile[1]
        age = profile[4]
        retirement_age = profile[5]
        annual_income = profile[8]
        annual_expenses = profile[9]
        current_assets = profile[10]
        risk_tolerance = profile[12]
        money_by_retirement = profile[13]
        interested_dividend = profile[14]
        market_cap_preference = profile[15]
        print("Main User Summary:")
        print(f"Name: {name}")
        print(f"Annual income: {annual_income:,.2f}")
        print(f"Annual expenses: {annual_expenses:,.2f}")
        print(f"Current assets: {current_assets:,.2f}")
        print(f"Risk profile: {risk_algorithm(risk_tolerance)}")
        print(f"Retirement goal in today's money: ฿{money_by_retirement:,.2f}")
        inflation_rate = 0.03  # test inflation rate
        adjusted_goal = inflation_adjustment(money_by_retirement, age, retirement_age, inflation_rate)
        monthly_savings_needed, remaining_amount, months_till_retirement = required_monthly_savings(adjusted_goal, current_assets, age, retirement_age)
        print(f"Inflation-adjusted retirement goal: {adjusted_goal:,.2f}")
        print(f"Monthly savings needed: {monthly_savings_needed:,.2f}")
        print(f"Remaining amount: {remaining_amount:,.2f}")
        print(f"Months until retirement: {months_till_retirement}")
        progress(annual_income, annual_expenses, monthly_savings_needed)

        print("Household Summary:")
        print(f"Members: {household_profile['members']}")
        print(f"Combined annual income: "f"฿{household_profile['annual_income']:,.2f}")
        print(f"Combined annual expenses: "f"฿{household_profile['annual_expenses']:,.2f}")
        print(f"Combined assets: "f"฿{household_profile['current_assets']:,.2f}")
        print(f"Household risk: "f"{risk_algorithm(household_profile['risk_tolerance'])}")

    connect.close()

if __name__ == "__main__":
    main()

