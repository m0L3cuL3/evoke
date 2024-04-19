from __future__ import unicode_literals
from decimal import Decimal
import frappe
import evoke.utils as utils

def execute(filters=None):
    data = get_data(filters)
    columns = get_columns()
    chart = get_chart(filters)

    return columns, data, None, chart

def get_columns():
    columns = [
        { "fieldname": "store_name", "label": "Store", "width": 200 },
        { "fieldname": "profit_loss", "label": "Profit / Loss", "fieldtype": "Currency", "width": 200 },
    ]
   
    return columns

def get_conditions(filters):
    if filters.get("evoke_cash_flow_filter"):
        dcf = filters.get("evoke_cash_flow_filter")
        conditions = f" WHERE t1.name = '{dcf}' "
    
    return conditions

def get_data(filters):
    dcf = filters.get("evoke_cash_flow_filter")
    data = []
    labels = []

    stores = frappe.db.sql(f"SELECT store_name FROM `tabStore`", as_dict=1)

    for row in stores:
        labels.append(row['store_name'])
        total_store_sales = frappe.db.sql(f"""SELECT SUM(t2.amount) AS total_sales_amount FROM `tabEvoke Cash Flow` AS t1 JOIN `tabDaily Cash Flow Item` AS t2 ON t1.name = t2.parent WHERE t1.name = '{dcf}' AND t2.store = '{row['store_name']}' AND t2.transaction = 'Income'""", as_dict=1)
        total_store_expenses = frappe.db.sql(f"""SELECT SUM(t2.amount) AS total_expenses_amount FROM `tabEvoke Cash Flow` AS t1 JOIN `tabDaily Cash Flow Item` AS t2 ON t1.name = t2.parent WHERE t1.name = '{dcf}' AND t2.store = '{row['store_name']}' AND t2.transaction = 'Expenses'""", as_dict=1)
        
        rental = 0
        administrative = utils.get_administrative_expenses_per_store(dcf)
        operational_expenses = utils.get_operational_expenses(dcf)

        total_sales = total_store_sales[0].total_sales_amount
        total_expenses = total_store_expenses[0].total_expenses_amount
        store_rental_rates = utils.get_store_rental_rates(row['store_name'])

        if total_sales == None:
            total_sales = 0
            administrative = 0
            operational_expenses = 0
        
        if total_expenses == None:
            total_expenses = 0

        if row['store_name'] == 'Online Sales':
            administrative = 0
            operational_expenses = 0

            
        if store_rental_rates[0].rental_rate == None:
            rental += 0
        else:
            rental += store_rental_rates[0].rental_rate

        profit_loss = total_sales - (total_expenses + rental + administrative + operational_expenses)

        if total_sales > total_expenses:
            data.append({ 'store_name': row['store_name'], 'profit_loss': round(profit_loss, 2) })
        else:
            data.append({ 'store_name': row['store_name'], 'profit_loss': -abs(round(profit_loss, 2)) })

    return data

def get_chart(filters):
    dcf = filters.get("evoke_cash_flow_filter")
    data = []
    labels = []
    colors = []

    stores = frappe.db.sql(f"SELECT store_name FROM `tabStore`", as_dict=1)

    for row in stores:
        labels.append(row['store_name'])
        total_store_sales = frappe.db.sql(f"""SELECT SUM(t2.amount) AS total_sales_amount FROM `tabEvoke Cash Flow` AS t1 JOIN `tabDaily Cash Flow Item` AS t2 ON t1.name = t2.parent WHERE t1.name = '{dcf}' AND t2.store = '{row['store_name']}' AND t2.transaction = 'Income'""", as_dict=1)
        total_store_expenses = frappe.db.sql(f"""SELECT SUM(t2.amount) AS total_expenses_amount FROM `tabEvoke Cash Flow` AS t1 JOIN `tabDaily Cash Flow Item` AS t2 ON t1.name = t2.parent WHERE t1.name = '{dcf}' AND t2.store = '{row['store_name']}' AND t2.transaction = 'Expenses'""", as_dict=1)
        
        rental = 0
        administrative = 15705.00 # temporary
        operational_expenses = utils.get_operational_expenses(dcf)

        total_sales = total_store_sales[0].total_sales_amount
        total_expenses = total_store_expenses[0].total_expenses_amount
        store_rental_rates = utils.get_store_rental_rates(row['store_name'])

        if total_sales == None:
            total_sales = 0
            administrative = 0
            operational_expenses = 0
        
        if total_expenses == None:
            total_expenses = 0

        if row['store_name'] == 'Online Sales':
            administrative = 0
            operational_expenses = 0

            
        if store_rental_rates[0].rental_rate == None:
            rental += 0
        else:
            rental += store_rental_rates[0].rental_rate

        profit_loss = total_sales - (total_expenses + rental + administrative + operational_expenses)

        if total_sales > total_expenses:
            data.append(round(profit_loss, 2))
        else:
            data.append(-abs(round(profit_loss, 2)))

    chart = { 'data': {'labels': labels, 'datasets': [{'values': data}]}, 'type': 'bar', 'colors': colors }

    chart['fieldtype'] = 'Currency'

    return chart
    