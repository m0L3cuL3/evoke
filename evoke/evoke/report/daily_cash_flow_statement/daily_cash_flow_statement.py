from __future__ import unicode_literals
from decimal import Decimal
import frappe

def execute(filters=None):
    data = get_data(filters)
    columns = get_columns(filters)
    chart = get_chart(filters)
    report_summary = get_report_summary(filters)

    # message = [
    #     f"The letters '<b>cats</b>' in numbers is <span style='color:Red;'>2287</span>",
    #     f"<br>",
    #     f"The letters '<b>dogs</b>' in numbers is <span style='color:Blue;'>3647</span>"
    # ]
    
    return columns, data, None, chart, report_summary

def get_columns(filters):
    columns = [
        { "fieldname": "store", "label": "Store", "width": 200 },
        { "fieldname": "day_date", "label": "Day", "fieldtype": "Date", "width": 200 },
        { "fieldname": "transaction", "label": "Transaction", "width": 120 },
        { "fieldname": "type", "label": "Type", "width": 120 },
        { "fieldname": "amount", "label": "Amount", "fieldtype": "Currency", "width": 120 },
        { "fieldname": "deposit", "label": "Deposit", "fieldtype": "Currency", "width": 120 },
        { "fieldname": "user_remarks", "label": "User Remarks", "width": 220 },
    ]
   
    return columns

def get_conditions(filters):
    if filters.get("evoke_cash_flow_filter"):
        dcf = filters.get("evoke_cash_flow_filter")
        conditions = f" WHERE t1.name = '{dcf}' "
    
    return conditions

def get_data(filters):
    conditions = get_conditions(filters)
    data = []
    sql_result = frappe.db.sql("SELECT t2.store, t2.day_date, t2.transaction, t2.type, t2.amount, t2.user_remarks FROM `tabEvoke Cash Flow` AS t1 JOIN `tabDaily Cash Flow Item` AS t2 ON t1.name = t2.parent" + conditions + "ORDER BY t2.day_date DESC, t2.store DESC, t2.transaction DESC", as_dict=1)

    for row in sql_result:
        if row['transaction'] == 'Income':
            sales = row['amount']
            incentives = 0
            # Find incentives if present
            for sub_row in sql_result:
                if sub_row['store'] == row['store'] and sub_row['day_date'] == row['day_date'] and sub_row['transaction'] == 'Expenses' and sub_row['type'] == 'Incentives':
                    incentives = sub_row['amount']
                    break
            
            deposit = sales - incentives
            r = {'store': row['store'], 'day_date': row['day_date'], 'transaction': row['transaction'], 'type': row['type'], 'amount': row['amount'], 'deposit': deposit, 'user_remarks': row['user_remarks']}
            data.append(r)
        else:
            r = {'store': row['store'], 'day_date': row['day_date'], 'transaction': row['transaction'], 'type': row['type'], 'amount': row['amount'], 'deposit': None, 'user_remarks': row['user_remarks']}
            data.append(r)

    return data
    

def get_report_summary(filters):
    conditions = get_conditions(filters)
    data = frappe.db.sql("SELECT t2.store, t2.day_date, t2.transaction, t2.type, t2.amount, t2.user_remarks FROM `tabEvoke Cash Flow` AS t1 JOIN `tabDaily Cash Flow Item` AS t2 ON t1.name = t2.parent" + conditions + "ORDER BY t2.day_date ASC, t2.store ASC, t2.transaction DESC", as_dict=1)
    
    sales = 0
    expenses = 0
    # product_cost = 0
    # operating_expenses = 0
    # marketing = 0
    # payroll = 0
    # incentives = 0

    for row in data:
        if row.transaction == 'Income':
            sales += row.amount
        if row.transaction == 'Expenses':
            expenses += row.amount
        # if row.type == 'Product Cost':
        #     product_cost += row.amount
        # if row.type == 'Operating Expenses':
        #     operating_expenses += row.amount
        # if row.type == 'Marketing':
        #     marketing += row.amount
        # if row.type == 'Payroll':
        #     payroll += row.amount
        # if row.type == 'Incentives':
        #     incentives += row.amount

    report_summary = [
        {"label":"Grand Total Sales","value": sales,'indicator':'Blue', "datatype": "Currency"},
        {"label":"Grand Total Expenses","value": expenses,'indicator':'Red', "datatype": "Currency"},
        {"label":"Grand Total Profit","value": 0,'indicator':'Green', "datatype": "Currency"},
        # {"label":"Total Product Cost","value": product_cost,'indicator':'Red', "datatype": "Currency"},
        # {"label":"Total Operating Expenses","value": operating_expenses,'indicator':'Red', "datatype": "Currency"},
        # {"label":"Total Marketing","value": marketing,'indicator':'Red', "datatype": "Currency"},
        # {"label":"Total Payroll","value": payroll,'indicator':'Red', "datatype": "Currency"},
        # {"label":"Total Incentives","value": incentives,'indicator':'Red', "datatype": "Currency"},
    ]

    return report_summary

def get_chart(filters):
    dcf = filters.get("evoke_cash_flow_filter")
    data = frappe.db.sql(f"SELECT store_name FROM `tabStore`", as_dict=1)
    labels = []
    sales = []
    expenses = []
    profit = []
    for row in data:
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

        
        
        profit.append(round(total_store_profit, 2))
        sales.append(round(total_sales, 2))
        expenses.append(round(total_expenses, 2))

        print(total_store_sales)

    chart = { 'data': {'labels': labels, 'datasets': [{'name': 'Income', 'values': sales}, {'name': 'Expenses', 'values': expenses}, {'name': 'Profit', 'values': profit}]}, 'type': 'bar', 'colors': ['blue', 'red', 'green'] }

    chart['fieldtype'] = 'Currency'

    return chart
