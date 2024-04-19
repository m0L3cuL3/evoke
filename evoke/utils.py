from __future__ import unicode_literals, division
import calendar
import frappe
from frappe import _

# Obtains specific store's rental rates
# Returns an array of objects
def get_store_rental_rates(store_name):
    store_rental_rates = frappe.db.get_all("Store", fields=['store_name', 'store_rental_rates.rental_date', 'store_rental_rates.rental_rate'], filters=dict(store_name=store_name))
    return store_rental_rates

def get_rental_rates(store_name):
    store_rental_rates = frappe.db.get_all("Store", fields=['store_name', 'store_rental_rates.rental_date', 'store_rental_rates.rental_rate', 'store_rental_rates.linked_cash_flow'], filters=dict(store_name=store_name))
    return store_rental_rates

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