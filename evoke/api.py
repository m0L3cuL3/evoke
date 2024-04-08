from datetime import datetime, timedelta
import frappe

@frappe.whitelist()
def get_days_of_month(date):
    # Convert input string to datetime object
    input_datetime = datetime.strptime(date, "%Y-%m-%d")

    # Get the year, month, and day from the input date
    year = input_datetime.year
    month = input_datetime.month
    day = input_datetime.day

    # Return the same date repeated 5 times
    return [datetime(year, month, day).strftime("%Y-%m-%d")] * 5

@frappe.whitelist()
def get_month_and_year(date):
    # Convert input string to datetime object
    input_datetime = datetime.strptime(date, "%Y-%m-%d")
    
    # Extract month and year from the input date and format them
    month = input_datetime.strftime("%B")  # Get full month name
    year = input_datetime.year
    
    return f"{month} {year}"
