from datetime import datetime, timedelta
import frappe

@frappe.whitelist()
def get_days_of_month(date):
    # Convert input string to datetime object
    input_datetime = datetime.strptime(date, "%Y-%m-%d")
    
    # Get the year and month from the input date
    year = input_datetime.year
    month = input_datetime.month
    
    # Calculate the number of days in the given month
    num_days = (datetime(year, month % 12 + 1, 1) - timedelta(days=1)).day
    
    # Store all the days of the month in a list
    days_of_month = []
    for day in range(1, num_days + 1):
        days_of_month.append(datetime(year, month, day).strftime("%Y-%m-%d"))
    
    return days_of_month

@frappe.whitelist()
def get_month_and_year(date):
    # Convert input string to datetime object
    input_datetime = datetime.strptime(date, "%Y-%m-%d")
    
    # Extract month and year from the input date and format them
    month = input_datetime.strftime("%B")  # Get full month name
    year = input_datetime.year
    
    return f"{month} {year}"
