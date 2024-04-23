from __future__ import unicode_literals, division
import calendar
from datetime import datetime
import frappe
from frappe import _

# Applies monthly rental rates of store
# Returns float number
def apply_monthly_rental_rates(store_name, initial_date):
    store_rental_rates = frappe.db.get_all("Store", fields=['store_name', 'store_rental_rates.rental_date', 'store_rental_rates.rental_rate'], filters=dict(store_name=store_name))
    for rate_obj in reversed(store_rental_rates):
        rental_date = rate_obj['rental_date']
        if rental_date is not None:
            if isinstance(rental_date, str):
                rental_date = datetime.strptime(rental_date, "%Y-%m-%d").date()  # Convert rental_date to datetime object
            if initial_date >= rental_date:
                return rate_obj['rental_rate']
    return None  # Return None if no matching rate is found

# Obtains calculated operational expenses per store
# Returns float number
def get_operational_expenses(dcf):
    operating_expense_result = frappe.db.sql(f"""SELECT SUM(t2.amount) AS operating_expenses_amount FROM `tabEvoke Cash Flow` AS t1 JOIN `tabDaily Cash Flow Item` AS t2 ON t1.name = t2.parent WHERE t1.name = '{dcf}' AND t2.store = 'Office / Warehouse' AND t2.type = 'Operating Expenses' AND t2.transaction = 'Expenses'""", as_dict=1)
    active_stores_result = frappe.db.sql(f"SELECT COUNT(store_name) AS active_stores FROM `tabStore` WHERE is_active = true", as_dict=1)

    operating_expense = operating_expense_result[0].operating_expenses_amount
    active_stores = active_stores_result[0].active_stores

    operational_expenses = operating_expense / active_stores
    return operational_expenses

# Obtains the grand total operational expenses
# Return float number
def get_total_operational_expenses(dcf):
    operating_expense_result = frappe.db.sql(f"""SELECT SUM(t2.amount) AS operating_expenses_amount FROM `tabEvoke Cash Flow` AS t1 JOIN `tabDaily Cash Flow Item` AS t2 ON t1.name = t2.parent WHERE t1.name = '{dcf}' AND t2.store = 'Office / Warehouse' AND t2.type = 'Operating Expenses' AND t2.transaction = 'Expenses'""", as_dict=1)

    operating_expense = operating_expense_result[0].operating_expenses_amount

    return operating_expense

# Obtains the calculated total administrative expenses per store
# Returns float number
def get_administrative_expenses(dcf):
    administrative_expense_result = frappe.db.sql(f"""SELECT administrative_expense, date FROM `tabEvoke Cash Flow` WHERE name = '{dcf}'""", as_dict=1)
    active_stores_result = frappe.db.sql(f"SELECT COUNT(store_name) AS active_stores FROM `tabStore` WHERE is_active = true", as_dict=1)

    year = administrative_expense_result[0].date.year
    month = administrative_expense_result[0].date.month
    days_in_month = calendar.monthrange(year, month)[1]

    # Get daily administrative expense
    expense = administrative_expense_result[0].administrative_expense / days_in_month

    # Grand total of administrative expense for active stores
    result = expense * active_stores_result[0].active_stores

    return result

# Obtains the total administrative expenses per store
# Returns float number
def get_administrative_expenses_per_store(dcf):
    administrative_expense_result = frappe.db.sql(f"""SELECT administrative_expense, date FROM `tabEvoke Cash Flow` WHERE name = '{dcf}'""", as_dict=1)

    year = administrative_expense_result[0].date.year
    month = administrative_expense_result[0].date.month
    days_in_month = calendar.monthrange(year, month)[1]

    result = administrative_expense_result[0].administrative_expense / days_in_month

    return result

def get_total_of_transaction_type(dcf, store_name, type, transaction, conditions):
    total_amount = frappe.db.sql(f"""SELECT SUM(t2.amount) AS total_amount FROM `tabEvoke Cash Flow` AS t1 JOIN `tabDaily Cash Flow Item` AS t2 ON t1.name = t2.parent WHERE t1.name = '{dcf}' AND t2.store = '{store_name}' AND t2.type = '{type}' AND t2.transaction = '{transaction}' {conditions} """, as_dict=1)
    result = total_amount[0].total_amount

    if result == None:
        result = 0

    return result