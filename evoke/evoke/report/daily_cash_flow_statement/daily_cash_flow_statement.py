from __future__ import unicode_literals
import frappe

from evoke.utilities.cash_flow.cash_flow import CashFlowUtils as cashflow_utils
from evoke.utilities.store.store import StoreUtils as store_utils

def execute(filters=None):
    data = get_data(filters)
    columns = get_columns()
    chart = get_chart(filters)
    report_summary = get_report_summary(filters)

    return columns, data, None, chart, report_summary

def get_filters(filters):
    if filters.get('date_from') and filters.get('date_to'):
        return [['day_date', 'between', [filters.get('date_from'), filters.get('date_to')]]]

def get_columns():
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

def get_data(filters):
    data = []
    filters = get_filters(filters)
    result = frappe.db.get_all(
        'Evoke Cash Flow',
        fields=[
            'daily_entries.store',
            'daily_entries.day_date',
            'daily_entries.transaction',
            'daily_entries.type',
            'daily_entries.amount',
            'daily_entries.user_remarks'
        ],
        filters=filters,
        order_by='day_date DESC, store DESC, transaction DESC'
    )

    for row in result:
        if row['transaction'] == 'Income':
            sales = row['amount']
            incentives = 0
            # Find incentives if present
            for sub_row in result:
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
    cashflow_details = frappe.db.get_all(
        'Evoke Cash Flow', 
        fields=[
            'date', 
            'month_year_entry'
        ], 
        filters=[
            # ['name', '=', month_year]
            ['day_date', 'between', [filters.get('date_from'), filters.get('date_to')]]
        ]
    )

    stores = frappe.db.get_all(
        "Store", 
        fields=[
            'store_name', 
            'store_rental_rates.rental_date', 
            'store_rental_rates.rental_rate'
        ], 
        group_by='store_name'
    )

    store_sales = frappe.db.get_all(
        'Evoke Cash Flow',
        fields=[
            'daily_entries.amount',
            'sum(amount) as total_sales_amount'
        ],
        filters=[
            ['transaction', '=', 'Income'],
            ['day_date', 'between', [filters.get('date_from'), filters.get('date_to')]]
        ]
    )

    store_expenses = frappe.db.get_all(
        'Evoke Cash Flow',
        fields=[
            'daily_entries.amount',
            'sum(amount) as total_expenses_amount'
        ],
        filters=[
            ['transaction', '=', 'Expenses'],
            ['day_date', 'between', [filters.get('date_from'), filters.get('date_to')]]
        ]
    )
    
    operational_expenses = cashflow_utils.get_total_operational_expenses(filters.get('date_from'), filters.get('date_to'))
    administrative_expense = cashflow_utils.get_administrative_expenses(filters.get('date_from'), filters.get('date_to'))
    sales = store_sales[0].total_sales_amount
    expenses = store_expenses[0].total_expenses_amount

    rental = 0

    for row in stores:
        if store_utils.apply_monthly_rental_rates(row['store_name'], cashflow_details[0]['date']) == None:
            rental += 0
        else:
            rental += store_utils.apply_monthly_rental_rates(row['store_name'], cashflow_details[0]['date'])

    if sales == None:
        sales = 0

    if expenses == None:
        expenses = 0

    if rental == None:
        rental = 0
    
    if administrative_expense == None:
        administrative_expense = 0

    if operational_expenses == None:
        operational_expenses = 0
    
    total_expenses = expenses + rental + administrative_expense + operational_expenses
    profit = sales - total_expenses


    report_summary = [
        {"label":"Grand Total Sales","value": sales,'indicator':'Blue', "datatype": "Currency"},
        {"label":"Grand Total Expenses","value": total_expenses,'indicator':'Red', "datatype": "Currency"},
        {"label":"Grand Total Profit","value": profit,'indicator':'Green', "datatype": "Currency"},
    ]

    return report_summary

def get_chart(filters):
    stores = frappe.db.get_all(
        'Store',
        fields=[
            'store_name'
        ],
        order_by='store_name DESC'
    )

    labels = []
    sales = []
    expenses = []
    profit = []
    
    for row in stores:
        labels.append(row['store_name'])

        store_sales = frappe.db.get_all(
            'Evoke Cash Flow',
            fields=[
                'daily_entries.amount',
                'sum(amount) as total_sales_amount'
            ],
            filters=[
                # ['name', '=', dcf],
                ['store', '=', row['store_name']],
                ['transaction', '=', 'Income'],
                ['day_date', 'between', [filters.get('date_from'), filters.get('date_to')]]
            ]
        )

        store_expenses = frappe.db.get_all(
            'Evoke Cash Flow',
            fields=[
                'daily_entries.amount',
                'sum(amount) as total_expenses_amount'
            ],
            filters=[
                # ['name', '=', dcf],
                ['store', '=', row['store_name']],
                ['transaction', '=', 'Expenses'],
                ['day_date', 'between', [filters.get('date_from'), filters.get('date_to')]]
            ]
        )

        total_sales = store_sales[0].total_sales_amount
        total_expenses = store_expenses[0].total_expenses_amount

        if total_expenses == None:
            total_expenses = 0

        if total_sales == None:
            total_store_profit = 0
            total_sales = 0
        else:
            total_store_profit = total_sales - total_expenses
        
        
        
        profit.append(round(total_store_profit, 2))
        sales.append(round(total_sales, 2))
        expenses.append(round(total_expenses, 2))

    chart = { 
        'data': {
            'labels': labels,
            'datasets': [
                {'name': 'Income', 'values': sales}, 
                {'name': 'Expenses', 'values': expenses}, 
                {'name': 'Profit', 'values': profit}
            ]
        }, 
        'type': 'bar', 
        'colors': [
            'blue', 
            'red', 
            'green'
        ] 
    }

    chart['fieldtype'] = 'Currency'

    return chart
