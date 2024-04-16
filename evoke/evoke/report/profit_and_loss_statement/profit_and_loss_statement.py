from __future__ import unicode_literals
from decimal import Decimal
import frappe

def execute(filters=None):
    data = get_data(filters)
    columns = get_columns()
    chart = get_chart(filters)
    message = 'Note: Calculations for profit/loss are currently in progress'

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
    stores = frappe.db.sql(f"SELECT store_name FROM `tabStore`", as_dict=1)
    labels = []
    profit = []
    for row in stores:
        labels.append(row['store_name'])
        total_store_sales = frappe.db.sql(f"""SELECT SUM(t2.amount) AS total_sales_amount FROM `tabEvoke Cash Flow` AS t1 JOIN `tabDaily Cash Flow Item` AS t2 ON t1.name = t2.parent WHERE t1.name = '{dcf}' AND t2.store = '{row['store_name']}' AND t2.transaction = 'Income'""", as_dict=1)
        total_store_expenses = frappe.db.sql(f"""SELECT SUM(t2.amount) AS total_expenses_amount FROM `tabEvoke Cash Flow` AS t1 JOIN `tabDaily Cash Flow Item` AS t2 ON t1.name = t2.parent WHERE t1.name = '{dcf}' AND t2.store = '{row['store_name']}' AND t2.transaction = 'Expenses'""", as_dict=1)
        
        total_sales = total_store_sales[0].total_sales_amount
        total_expenses = total_store_expenses[0].total_expenses_amount

        if total_sales == None:
            total_store_profit = 0
            total_sales = 0
        else:
            total_store_profit = total_sales - total_expenses
        
        if total_expenses == None:
            total_expenses = 0

        if total_sales > total_expenses:
            data.append({ 'store_name': row['store_name'], 'profit_loss': round(total_sales, 2) })
        else:
            data.append({ 'store_name': row['store_name'], 'profit_loss': -abs(round(total_expenses, 2)) })
        
        profit.append(round(total_store_profit, 2))

    return data

def get_chart(filters):
    dcf = filters.get("evoke_cash_flow_filter")
    data = []
    stores = frappe.db.sql(f"SELECT store_name FROM `tabStore`", as_dict=1)
    labels = []
    profit = []
    for row in stores:
        labels.append(row['store_name'])
        total_store_sales = frappe.db.sql(f"""SELECT SUM(t2.amount) AS total_sales_amount FROM `tabEvoke Cash Flow` AS t1 JOIN `tabDaily Cash Flow Item` AS t2 ON t1.name = t2.parent WHERE t1.name = '{dcf}' AND t2.store = '{row['store_name']}' AND t2.transaction = 'Income'""", as_dict=1)
        total_store_expenses = frappe.db.sql(f"""SELECT SUM(t2.amount) AS total_expenses_amount FROM `tabEvoke Cash Flow` AS t1 JOIN `tabDaily Cash Flow Item` AS t2 ON t1.name = t2.parent WHERE t1.name = '{dcf}' AND t2.store = '{row['store_name']}' AND t2.transaction = 'Expenses'""", as_dict=1)
        
        total_sales = total_store_sales[0].total_sales_amount
        total_expenses = total_store_expenses[0].total_expenses_amount

        if total_sales == None:
            total_store_profit = 0
            total_sales = 0
        else:
            total_store_profit = total_sales - total_expenses
        
        if total_expenses == None:
            total_expenses = 0

        if total_sales > total_expenses:
            data.append(round(total_sales, 2))
        else:
            data.append(-abs(round(total_expenses, 2)))
        
        profit.append(round(total_store_profit, 2))

    chart = { 'data': {'labels': labels, 'datasets': [{'name': 'Profit', 'values': data}]}, 'type': 'bar', 'colors': ['pink'] }

    chart['fieldtype'] = 'Currency'

    return chart
    