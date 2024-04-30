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

@frappe.whitelist()
def get_stores():
    stores = frappe.db.get_all("Store", fields=['store_name'])

    return stores

@frappe.whitelist()
def get_cash_flow_initial_date(cash_flow):
    date = frappe.get_doc('Evoke Cash Flow', cash_flow)

    return date

@frappe.whitelist()
def get_deposits_per_store(cash_flow_entry, transaction_date):
    deposits = []
    data = frappe.db.sql(f"""
        SELECT 
            t2.day_date, 
            t2.store, 
            t2.transaction, 
            t2.type, 
            t2.amount 
        FROM `tabEvoke Cash Flow` AS t1
        JOIN `tabDaily Cash Flow Item` AS t2
        ON t1.name = t2.parent
        WHERE t1.name = '{cash_flow_entry}'
        AND t2.day_date = '{transaction_date}'
        AND NOT t2.store = 'Online Sales'
        AND NOT t2.store = 'Office / Warehouse'
        ORDER BY t2.day_date ASC, t2.store DESC, t2.transaction DESC
    """, as_dict=1)

    for row in data:
        if row['transaction'] == 'Income':
            sales = row['amount']
            incentives = 0

            for sub_row in data:
                if sub_row['store'] == row['store'] and sub_row['day_date'] == row['day_date'] and sub_row['transaction'] == 'Expenses' and sub_row['type'] == 'Incentives':
                    incentives = sub_row['amount']
                    break

            deposit = sales - incentives
            r = {'day_date': row['day_date'], 'store': row['store'], 'deposit': deposit}
            deposits.append(r)

    return deposits
