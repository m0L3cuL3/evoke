from __future__ import unicode_literals
import frappe
from evoke.utilities.profit_loss.profit_loss import ProfitLossUtils as profit_loss_utils
from evoke.utilities.store.store import StoreUtils as store_utils

def execute(filters=None):
    data = get_data(filters)
    columns = get_columns()

    return columns, data, None

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

def get_data(filters):
    data = []
    labels = []

    stores = frappe.db.get_all(
        'Store',
        fields=[
            'store_name'
        ],
        filters=[],
        order_by='store_name DESC'
    )

    cashflow_details = frappe.db.get_all(
        'Evoke Cash Flow', 
        fields=['date', 'month_year_entry'], 
        filters=[
            ['day_date', 'between', [filters.get('date_from'), filters.get('date_to')]]
        ]
    )

    for row in stores:
        labels.append(row['store_name'])
        
        store_sales = frappe.db.get_all(
            'Evoke Cash Flow',
            fields=[
                'daily_entries.amount',
                'sum(amount) as total_sales_amount'
            ],
            filters=[
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
                ['store', '=', row['store_name']],
                ['transaction', '=', 'Expenses'],
                ['day_date', 'between', [filters.get('date_from'), filters.get('date_to')]]
            ]
        )

        rental = 0
        administrative = profit_loss_utils.get_administrative_expenses_per_store(filters)
        operational_expenses = profit_loss_utils.get_operational_expenses(filters)

        total_sales = store_sales[0].total_sales_amount
        total_expenses = store_expenses[0].total_expenses_amount
        total_incentives = profit_loss_utils.get_total_of_transaction_type(
            row['store_name'],
            'Incentives', 
            'Expenses', 
            filters
        )
        total_marketing = profit_loss_utils.get_total_of_transaction_type(
            row['store_name'], 
            'Marketing', 
            'Expenses', 
            filters
        )
        total_operating_expense = profit_loss_utils.get_total_of_transaction_type(
            row['store_name'], 
            'Operating Expenses', 
            'Expenses', 
            filters
        )
        total_payroll = profit_loss_utils.get_total_of_transaction_type(
            row['store_name'], 
            'Payroll', 
            'Expenses', 
            filters
        )
        total_product_cost = profit_loss_utils.get_total_of_transaction_type(
            row['store_name'], 
            'Product Cost', 
            'Expenses', 
            filters
        )

        if total_sales == None:
            total_sales = 0
            administrative = 0
            operational_expenses = 0
        
        if total_expenses == None:
            total_expenses = 0

        if row['store_name'] == 'Online Sales':
            administrative = 0
            operational_expenses = 0

        if cashflow_details:
            if store_utils.apply_monthly_rental_rates(row['store_name'], cashflow_details[0]['date']) == None:
                rental += 0
            else:
                rental += store_utils.apply_monthly_rental_rates(row['store_name'], cashflow_details[0]['date'])
        else:
            rental += 0
        

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
    