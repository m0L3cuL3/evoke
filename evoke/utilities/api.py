from datetime import datetime
from frappe.utils import add_to_date
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
def get_deposits_per_store(transaction_date):
    deposits = []
    data = frappe.db.get_all(
        'Evoke Cash Flow',
        fields=[
            'daily_entries.day_date',
            'daily_entries.store',
            'daily_entries.transaction',
            'daily_entries.type',
            'daily_entries.amount'
        ],
        filters=[
            ['store', '!=', 'Online Sales'],
            ['store', '!=', 'Office / Warehouse'],
            ['day_date', '=', transaction_date]
        ],
        order_by='day_date DESC, store DESC, transaction DESC'
    )

    for row in data:
        if row['transaction'] == 'Income':
            sales = row['amount']
            incentives = 0

            for sub_row in data:
                if sub_row['store'] == row['store'] and sub_row['day_date'] == row['day_date'] and sub_row['transaction'] == 'Expenses' and sub_row['type'] == 'Incentives':
                    incentives = sub_row['amount']
                    break

            store_deposits = frappe.db.get_all(
                'Deposit',
                fields=[
                    'name',
                    'depository_date',
                    'transaction_date',
                    'deposits.store',
                    'deposits.over_short_amount',
                    'deposits.for_deposit_amount',
                    'deposits.accumulated_amount'
                ],
                filters=[
                    ['store', '=', row['store']],
                    ['depository_date', '=', transaction_date]
                ]                      
            )

            if store_deposits:
                over_short_amount = store_deposits[0].over_short_amount
                accumulated_amount = store_deposits[0].accumulated_amount
            else:
                over_short_amount = 0
                accumulated_amount = 0

            deposit = sales - incentives

            if over_short_amount < 0:
                deposit = deposit + abs(over_short_amount)
            else:
                deposit = deposit - over_short_amount

            r = {
                'day_date': row['day_date'], 
                'store': row['store'], 
                'over_short_amount': over_short_amount,
                'accumulated_amount': accumulated_amount, 
                'for_deposit_amount': round(deposit, 2)
            }
            deposits.append(r)

    return deposits


@frappe.whitelist()
def get_accumulated_deposits():
    data = frappe.db.get_all('Deposit', fields=[
            'deposits.deposit_date',
            'deposits.transaction_date',
            'deposits.store',
            'deposits.over_short_amount',
            'deposits.for_deposit_amount',
            'deposits.amount_credited',
            'deposits.is_short',
            'deposits.is_deposited'
        ]
    )
    return data