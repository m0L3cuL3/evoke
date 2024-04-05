from __future__ import unicode_literals
import frappe

def execute(filters=None):
    data = get_data(filters)
    columns = get_columns(filters)
    report_summary = get_report_summary(filters)
    
    return columns, data, None, None, report_summary

def get_columns(filters):
    columns = [
        { "fieldname": "store", "label": "Store", "width": 200 },
        { "fieldname": "month_year_entry", "label": "Entry", "fieldtype": "Data", "width": 160 },
        { "fieldname": "day_date", "label": "Day", "fieldtype": "Date", "width": 120 },
        { "fieldname": "transaction", "label": "Transaction", "width": 120 },
        { "fieldname": "type", "label": "Type", "width": 120 },
        { "fieldname": "amount", "label": "Amount", "fieldtype": "Currency", "width": 120 },
        { "fieldname": "deposit", "label": "Deposit", "fieldtype": "Currency", "width": 120 },
        { "fieldname": "user_remarks", "label": "User Remarks", "width": 220 },
    ]

    return columns

def get_conditions(filters):
    if filters.get("daily_cash_flow_filter"):
        dcf = filters.get("daily_cash_flow_filter")
        conditions = f" WHERE t1.name = '{dcf}' "
    
    return conditions

def get_data(filters):
    conditions = get_conditions(filters)
    data = []
    sql_result = frappe.db.sql("SELECT t1.store, t1.month_year_entry, t2.day_date, t2.transaction, t2.type, t2.amount, t2.user_remarks FROM `tabDaily Cash Flow` AS t1 JOIN `tabDaily Cash Flow Item` AS t2 ON t1.name = t2.parent" + conditions + "ORDER BY t2.day_date ASC", as_dict=1)

    for row in sql_result:
        if row['transaction'] == 'Income':
            sales = row['amount']
            incentives = 0
            # Find incentives if present
            for sub_row in sql_result:
                if sub_row['day_date'] == row['day_date'] and sub_row['transaction'] == 'Expenses' and sub_row['type'] == 'Incentives':
                    incentives = sub_row['amount']
                    break
            deposit = sales - incentives
            r = {'store': row['store'], 'month_year_entry': row['month_year_entry'], 'day_date': row['day_date'], 'transaction': row['transaction'], 'type': row['type'], 'amount': row['amount'], 'deposit': deposit, 'user_remarks': row['user_remarks']}
            data.append(r)
        else:
            r = {'store': row['store'], 'month_year_entry': row['month_year_entry'], 'day_date': row['day_date'], 'transaction': row['transaction'], 'type': row['type'], 'amount': row['amount'], 'deposit': None, 'user_remarks': row['user_remarks']}
            data.append(r)

    return data

def get_report_summary(filters):
    conditions = get_conditions(filters)
    data = frappe.db.sql("SELECT t1.store, t1.month_year_entry, t2.day_date, t2.transaction, t2.type, t2.amount, t2.user_remarks FROM `tabDaily Cash Flow` AS t1 JOIN `tabDaily Cash Flow Item` AS t2 ON t1.name = t2.parent" + conditions + "ORDER BY t2.day_date ASC", as_dict=1)
    
    sales = 0
    product_cost = 0
    operating_expenses = 0
    marketing = 0
    payroll = 0
    incentives = 0

    for row in data:
        if row.type == 'Sales':
            sales += row.amount
        if row.type == 'Product Cost':
            product_cost += row.amount
        if row.type == 'Operating Expenses':
            operating_expenses += row.amount
        if row.type == 'Marketing':
            marketing += row.amount
        if row.type == 'Payroll':
            payroll += row.amount
        if row.type == 'Incentives':
            incentives += row.amount

    report_summary = [
        {"label":"Total Sales","value": sales,'indicator':'Green', "datatype": "Currency"},
        {"label":"Total Product Cost","value": product_cost,'indicator':'Red', "datatype": "Currency"},
        {"label":"Total Operating Expenses","value": operating_expenses,'indicator':'Red', "datatype": "Currency"},
        {"label":"Total Marketing","value": marketing,'indicator':'Red', "datatype": "Currency"},
        {"label":"Total Payroll","value": payroll,'indicator':'Red', "datatype": "Currency"},
        {"label":"Total Incentives","value": incentives,'indicator':'Red', "datatype": "Currency"},
    ]

    return report_summary