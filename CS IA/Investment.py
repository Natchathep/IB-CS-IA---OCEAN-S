import requests
import pandas as pd
import matplotlib as plt
import sys
from User_profile import create_database, get_user_profile, get_linked_profiles, create_household_profile, tax, inflation_adjustment, required_monthly_savings

def calculate_available_monthly_investment(main_profile, linked_profiles):
    main_income = main_profile[8]
    total_after_tax_income = main_income - tax(main_income)
    total_expenses = main_profile[9]

    for linked_profile in linked_profiles:
        linked_income = linked_profile[8]
        total_after_tax_income += linked_income - tax(linked_income)
        total_expenses += linked_profile[9]

    disposable_income = total_after_tax_income - total_expenses

    chosen_monthly = (disposable_income / 12)*(main_profile[16] / 100)

    if chosen_monthly < 0:
        chosen_monthly = 0

    return chosen_monthly

connect, cursor = create_database()

try:
    user_id = int(input("Enter profile ID: "))
    profile = get_user_profile(cursor, user_id)
except ValueError:
    print("ID must be an integer")
    connect.close()
    sys.exit(0)

if profile is None:
    print("Profile Not Found")
    connect.close()
    sys.exit(0)

print(profile)

linked_profiles = get_linked_profiles(cursor,user_id)

print("Linked profiles:", linked_profiles)

overall_profile = create_household_profile(profile,linked_profiles)

chosen_monthly = calculate_available_monthly_investment(profile, linked_profiles)

print(f"Chosen monthly investment: {chosen_monthly:,.2f}")

API_KEY = "CB6AA7DJDNZURUXD"

def get_stock_data(symbol, api_key):
    url = "https://www.alphavantage.co/query"
    params = {
        "function": "OVERVIEW",
        "symbol": symbol,
        "apikey": api_key
    }

    response = requests.get(url, params=params)
    data = response.json()

    try:
        beta = float(data.get("Beta"))
        market_capitalization = float(data.get("MarketCapitalization"))
    except (TypeError, ValueError):
        print("No data")
        return None

    risk = int
    if beta <0.8:
        risk = 1
    elif beta >= 0.8 and beta <= 1.2:
        risk = 2
    elif beta > 1.2:
        risk = 3

    market_cap = int
    if market_capitalization > 10000000000:
        market_cap = 1
    elif market_capitalization < 10000000000 and market_capitalization > 2000000000:
        market_cap = 2
    elif market_capitalization < 2000000000 and market_capitalization > 250000000:
        market_cap = 3

    Ticker = symbol
    company_Name = data.get("Name")
    sector = data.get("Sector")
    api_Dividend = data.get("DividendYield")

    if api_Dividend == "None" or api_Dividend is None:
        dividend = 0.0
    else:
        dividend = float(api_Dividend) * 100

    stock = {
    "ticker": symbol,
    "company_name": company_Name,
    "sector": sector,
    "dividend_yield": dividend,
    "market_cap": market_cap,
    "risk": risk
}
    return stock

'''
def get_stock_growth(symbol, api_key):
    url = "https://www.alphavantage.co/query"

    params = {
        "function" : "TIME_SERIES_MONTHLY",
        "symbol" : symbol,
        "apikey": api_key

    }

    response = requests.get(url, params=params)
    data = response.json()

    monthly_data = data.get("Monthly Time Series")
    
    dates = sorted(monthly_data(), reverse=True)

    current_month = monthly_data.get(dates[0])
    previous_month = monthly_data.get(dates[1])

    current_price = float(current_month.get("4. adjusted close"))
    previous_price = float(previous_month.get("4. adjusted close"))

    monthly_growth = (
    (current_price - previous_price)/ previous_price) * 100

    return monthly_growth'''

# Matching:
# Risk = 30%, exact match = 30, one away = 15, no = 0
# Sector = 10%, exact match = 10, not = 0
# Dividend = 30%, exact match = 30, -1% = 15, >1 = 0
# Growth = 20%, exact match = 20, -5% = 10, not = 0 
# Market Cap = 10%, exact match = 10, one away = 5, no = 0 

risk_tolerance = overall_profile["risk_tolerance"]
interested_sector = overall_profile["interested_sector"]
interested_dividend = overall_profile["interested_dividend"]
interested_marketcap = overall_profile["market_cap_preference"]

annual_income = overall_profile["annual_income"]
annual_expenses = overall_profile["annual_expenses"]
current_assets = overall_profile["current_assets"]
age = overall_profile["age"]
retirement_age = overall_profile["retirement_age"]
money_by_retirement = overall_profile["money_by_retirement"]

inflation_rate = 0.03

adjusted_goal = inflation_adjustment(
    money_by_retirement,
    age,
    retirement_age,
    inflation_rate
)

required_monthly, remaining_amount, months_remaining = (
    required_monthly_savings(
        adjusted_goal,
        current_assets,
        age,
        retirement_age
    )
)

print(f"Inflation-adjusted goal: ฿{adjusted_goal:,.2f}")
print(f"Household assets: ฿{current_assets:,.2f}")
print(f"Remaining amount: ฿{remaining_amount:,.2f}")
print(f"Months until retirement: {months_remaining}")
print(f"Required monthly savings: ฿{required_monthly:,.2f}")

difference = chosen_monthly - required_monthly

if difference < 0:
    print(f"Household is below the monthly target by {abs(difference):,.2f}")
elif difference > 0:
    print(f"Household is above the monthly target by {difference:,.2f}")
else:
    print("Household is exactly on target.")

def calculate_projected_value(current_assets, monthly_investment, months_remaining, annual_growth):
    projected_value_of_assets = current_assets

    monthly_growth_rate = ((1 + annual_growth / 100) ** (1 / 12)) - 1

    for month in range(months_remaining):
        projected_value_of_assets += monthly_investment
        projected_value_of_assets *= 1 + monthly_growth_rate

    return projected_value_of_assets

def calculate_growth_match(projected_value, adjusted_goal):

    if adjusted_goal <= 0:
        return 100

    growth_match = (projected_value / adjusted_goal)*100

    growth_match = max(0, min(growth_match, 100))

    return growth_match

def calculate_preference_match(risk_tolerance, interested_sector, interested_dividend, interested_marketcap, stock):
    match = 0
    risk_difference = abs(risk_tolerance - stock["risk"])
    if risk_difference == 0:
        match += 40
    elif risk_difference == 1:
        match += 20
    else:
        match += 0

    if interested_sector.lower() == stock["sector"].lower():
        match += 10
    else:
        match += 0

    if stock["dividend_yield"] >= interested_dividend:
        match += 40
    elif stock["dividend_yield"] >= interested_dividend - 1:
        match += 20
    else:
        match += 0

    market_cap_difference = abs(interested_marketcap - stock["market_cap"])
    if market_cap_difference == 0:
        match += 10
    elif market_cap_difference == 1:
        match += 5
    else:
        match += 0

    return match



#monthly_growth = get_stock_growth("AAPL", API_KEY)

def recommendation_explanation(risk_tolerance, interested_sector, interested_dividend, interested_marketcap, stock):
    explaination = []
    if interested_sector.lower() == stock["sector"].lower():
        explaination.append("Matches your sector preference")
    if risk_tolerance == stock["risk"]:
        explaination.append("Matches your risk tolerance")
    if stock["dividend_yield"] >= interested_dividend:
        explaination.append("Matches your dividend preferences")
    if interested_marketcap == stock["market_cap"]:
        explaination.append("Matches your market cap preference")

    return explaination

test_stocks = [
    {
        "ticker": "TEST_HIGH",
        "company_name": "High Growth Company",
        "sector": "Technology",
        "dividend_yield": 5.0,
        "market_cap": 3,
        "risk": 1,
        "growth": 7
    },
    {
        "ticker": "TEST_MEDIUM",
        "company_name": "Medium Growth Strong Match Company",
        "sector": "Technology",
        "dividend_yield": 5.0,
        "market_cap": 1,
        "risk": 3,
        "growth": 5
    },
    {
        "ticker": "TEST_LOW",
        "company_name": "Low Growth Company",
        "sector": "Financial Services",
        "dividend_yield": 1.0,
        "market_cap": 1,
        "risk": 3,
        "growth": 3
    }
]

user_stocks = ["AAPL", "TSLA", "V", "NVDA"]

scored_stocks = []

for stock in test_stocks:
    preference_match = calculate_preference_match(risk_tolerance, interested_sector, interested_dividend, interested_marketcap, stock)
    projected_value = calculate_projected_value(current_assets, chosen_monthly, months_remaining, stock["growth"])
    growth_match = calculate_growth_match(projected_value, adjusted_goal)
    

    stock["projected_value"] = projected_value
    stock["growth_match"] = growth_match
    stock["preference_match"] = preference_match
    final_score = (growth_match * 0.4) + (preference_match * 0.6)
    stock["final_score"] = final_score

    print(f"{stock['company_name']}: Growth match = {stock['growth_match']:.2f}%")
    print(f"{stock['company_name']}: Preference match = {stock['preference_match']:.2f}%")
    print(f"{stock['company_name']}: Final score = {stock['final_score']:.2f}%")
    scored_stocks.append(stock)

ranked_stocks = sorted(scored_stocks, key=lambda stock: stock["final_score"], reverse=True)

total_percent = 0
port_allocation = 0

for stock in scored_stocks:
    print(
        stock["company_name"],
        f"Projected value: ฿{stock['projected_value']:,.2f}"
    )

for stock in ranked_stocks:
    print(f"Company Name: {stock['company_name']}, match% : {calculate_preference_match(risk_tolerance, interested_sector, interested_dividend, interested_marketcap, stock)}")

    print(recommendation_explanation(risk_tolerance, interested_sector, interested_dividend, interested_marketcap, stock))

    total_percent += stock["final_score"]

print("Overall profile:", overall_profile)

for stock in ranked_stocks:
    port_allocation = ((stock["final_score"])/total_percent)*100
    monthly_stock_amount = chosen_monthly * (port_allocation / 100)
    stock["allocation_percentage"] = port_allocation
    stock["monthly_investment"] = monthly_stock_amount

    print(f"{stock['company_name']}:"
    f"{port_allocation:.2f}% allocation, "
    f"฿{monthly_stock_amount:,.2f} per month")

connect.close()
