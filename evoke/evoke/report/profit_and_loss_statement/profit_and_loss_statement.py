from __future__ import unicode_literals
from decimal import Decimal
import frappe
import evoke.utils as utils

def execute(filters=None):
    data = get_data(filters)
    columns = get_columns()
    # chart = get_chart(filters)
    message = [
        '<p class="alert alert-info">Do note when filtering make sure you are within the cash flow date range.</p>',
        '<p class="alert alert-warning"><strong>Example:</strong> Date <strong>FROM</strong> and <strong>TO</strong> should be within March 2024.</p>',
    ]

    return columns, data, message

def get_columns():
    columns = [
        { "fieldname": "store_name", "label": "Store", "width": 150 },
        { "fieldname": "incentives", "label": "Incentives", "fieldtype": "Currency", "width": 150 },
        { "fieldname": "marketing", "label": "Marketing", "fieldtype": "Currency", "width": 150 },
        { "fieldname": "operating_expenses", "label": "Operating Expenses", "fieldtype": "Currency", "width": 150 },
        { "fieldname": "payroll", "label": "Payroll", "fieldtype": "Currency", "width": 150 },
        { "fieldname": "product_cost", "label": "Product Cost", "fieldtype": "Currency", "width": 150 },
        { "fieldname": "sales", "label": "Sales", "fieldtype": "Currency", "width": 150 },
        { "fieldname": "profit_loss", "label": "Profit / Loss", "fieldtype": "Currency", "width": 150 },
    ]
   
    return columns

def get_conditions(filters):
    conditions = ""

    if filters.get("evoke_date_select_filter") == '':
        conditions = f""
    
    if filters.get("evoke_date_select_filter") == 'Today':
        date_from = filters.get("evoke_date_from")
        date_to = filters.get("evoke_date_to")
        conditions = f" AND t2.day_date BETWEEN '{date_from}' AND '{date_to}' "

    if filters.get("evoke_date_select_filter") == 'Yesterday':
        date_from = filters.get("evoke_date_from")
        date_to = filters.get("evoke_date_to")
        conditions = f" AND t2.day_date BETWEEN '{date_from}' AND '{date_to}' "

    if filters.get("evoke_date_select_filter") == 'Past 7 Days':
        date_from = filters.get("evoke_date_from")
        date_to = filters.get("evoke_date_to")
        conditions = f" AND t2.day_date BETWEEN '{date_from}' AND '{date_to}' "
    
    if filters.get("evoke_date_select_filter") == 'Past 30 Days':
        date_from = filters.get("evoke_date_from")
        date_to = filters.get("evoke_date_to")
        conditions = f" AND t2.day_date BETWEEN '{date_from}' AND '{date_to}' "

    if filters.get("evoke_date_select_filter") == 'Date Range':
        date_from = filters.get("evoke_date_from")
        date_to = filters.get("evoke_date_to")
        conditions = f" AND t2.day_date BETWEEN '{date_from}' AND '{date_to}' "
    

    return conditions

def get_data(filters):
    dcf = filters.get("evoke_cash_flow_filter")
    conditions = get_conditions(filters)
    data = []
    labels = []

    stores = frappe.db.sql(f"SELECT store_name FROM `tabStore`", as_dict=1)
    cashflow_details = frappe.db.get_all('Evoke Cash Flow', fields=['date', 'month_year_entry'], filters=[['name', '=', dcf]])

    for row in stores:
        labels.append(row['store_name'])
        
        total_store_sales = frappe.db.sql(f"""SELECT SUM(t2.amount) AS total_sales_amount FROM `tabEvoke Cash Flow` AS t1 JOIN `tabDaily Cash Flow Item` AS t2 ON t1.name = t2.parent WHERE t1.name = '{dcf}' AND t2.store = '{row['store_name']}' AND t2.transaction = 'Income' {conditions} """, as_dict=1)
        total_store_expenses = frappe.db.sql(f"""SELECT SUM(t2.amount) AS total_expenses_amount FROM `tabEvoke Cash Flow` AS t1 JOIN `tabDaily Cash Flow Item` AS t2 ON t1.name = t2.parent WHERE t1.name = '{dcf}' AND t2.store = '{row['store_name']}' AND t2.transaction = 'Expenses' {conditions} """, as_dict=1)

        rental = 0
        administrative = utils.get_administrative_expenses_per_store(dcf)
        operational_expenses = utils.get_operational_expenses(dcf)

        total_sales = total_store_sales[0].total_sales_amount
        total_expenses = total_store_expenses[0].total_expenses_amount
        total_incentives = utils.get_total_of_transaction_type(dcf, row['store_name'], 'Incentives', 'Expenses', conditions)
        total_marketing = utils.get_total_of_transaction_type(dcf, row['store_name'], 'Marketing', 'Expenses', conditions)
        total_operating_expense = utils.get_total_of_transaction_type(dcf, row['store_name'], 'Operating Expenses', 'Expenses', conditions)
        total_payroll = utils.get_total_of_transaction_type(dcf, row['store_name'], 'Payroll', 'Expenses', conditions)
        total_product_cost = utils.get_total_of_transaction_type(dcf, row['store_name'], 'Product Cost', 'Expenses', conditions)

        if total_sales == None:
            total_sales = 0
            administrative = 0
            operational_expenses = 0
        
        if total_expenses == None:
            total_expenses = 0

        if row['store_name'] == 'Online Sales':
            administrative = 0
            operational_expenses = 0

            
        if utils.apply_monthly_rental_rates(row['store_name'], cashflow_details[0]['date']) == None:
            rental += 0
        else:
            rental += utils.apply_monthly_rental_rates(row['store_name'], cashflow_details[0]['date'])

        profit_loss = total_sales - (total_expenses + rental + administrative + operational_expenses)

        if total_sales > total_expenses:
            data.append({ 
                'store_name': row['store_name'], 
                'incentives': round(total_incentives, 2), 
                'marketing': round(total_marketing, 2), 
                'operating_expenses': round(total_operating_expense, 2), 
                'payroll': round(total_payroll, 2), 
                'product_cost': round(total_product_cost, 2), 
                'sales': round(total_sales, 2),
                'profit_loss': round(profit_loss, 2) 
            })
        else:
            data.append({ 
                'store_name': row['store_name'], 
                'incentives': round(total_incentives, 2), 
                'marketing': round(total_marketing, 2), 
                'operating_expenses': round(total_operating_expense, 2), 
                'payroll': round(total_payroll, 2), 
                'product_cost': round(total_product_cost, 2), 
                'sales': round(total_sales, 2),
                'profit_loss': -abs(round(profit_loss, 2)) 
            })

    return data

# def get_chart(filters):
#     dcf = filters.get("evoke_cash_flow_filter")
#     data = []
#     labels = []
#     colors = []

#     stores = frappe.db.sql(f"SELECT store_name FROM `tabStore`", as_dict=1)

#     for row in stores:
#         labels.append(row['store_name'])
#         total_store_sales = frappe.db.sql(f"""SELECT SUM(t2.amount) AS total_sales_amount FROM `tabEvoke Cash Flow` AS t1 JOIN `tabDaily Cash Flow Item` AS t2 ON t1.name = t2.parent WHERE t1.name = '{dcf}' AND t2.store = '{row['store_name']}' AND t2.transaction = 'Income'""", as_dict=1)
#         total_store_expenses = frappe.db.sql(f"""SELECT SUM(t2.amount) AS total_expenses_amount FROM `tabEvoke Cash Flow` AS t1 JOIN `tabDaily Cash Flow Item` AS t2 ON t1.name = t2.parent WHERE t1.name = '{dcf}' AND t2.store = '{row['store_name']}' AND t2.transaction = 'Expenses'""", as_dict=1)
        
#         rental = 0
#         administrative = 15705.00 # temporary
#         operational_expenses = utils.get_operational_expenses(dcf)

#         total_sales = total_store_sales[0].total_sales_amount
#         total_expenses = total_store_expenses[0].total_expenses_amount
#         store_rental_rates = utils.get_store_rental_rates(row['store_name'])

#         if total_sales == None:
#             total_sales = 0
#             administrative = 0
#             operational_expenses = 0
        
#         if total_expenses == None:
#             total_expenses = 0

#         if row['store_name'] == 'Online Sales':
#             administrative = 0
#             operational_expenses = 0

            
#         if store_rental_rates[0].rental_rate == None:
#             rental += 0
#         else:
#             rental += store_rental_rates[0].rental_rate

#         profit_loss = total_sales - (total_expenses + rental + administrative + operational_expenses)

#         if total_sales > total_expenses:
#             data.append(round(profit_loss, 2))
#         else:
#             data.append(-abs(round(profit_loss, 2)))

#     chart = { 'data': {'labels': labels, 'datasets': [{'values': data}]}, 'type': 'bar', 'colors': colors }

#     chart['fieldtype'] = 'Currency'

#     return chart
    