import frappe
import calendar

class CashFlowUtils:
    def get_total_operational_expenses(date_from, date_to):
        operational_expenses = frappe.db.get_all(
            'Evoke Cash Flow',
            fields=[
                'daily_entries.amount',
                'sum(amount) as operating_expenses_amount'
            ],
            filters=[
                ['day_date', 'between', [date_from, date_to]],
                ['store', '=', 'Office / Warehouse'],
                ['type', '=', 'Operating Expenses'],
                ['transaction', '=', 'Expenses']
            ]
        )

        operating_expense = operational_expenses[0].operating_expenses_amount

        if operating_expense == None:
            operating_expense = 0

        return operating_expense
    
    def get_administrative_expenses(date_from, date_to):
        administrative_expense = frappe.db.get_all(
            'Evoke Cash Flow',
            fields=[
                'administrative_expense',
                'date'
            ],
            filters=[
               ['day_date', 'between', [date_from, date_to]]
            ]
        )

        active_stores = frappe.db.get_all(
            'Store',
            fields=[
                'count(store_name) as active_stores'
            ],
            filters=[
                ['is_active', '=', True]
            ]
        )

        year = administrative_expense[0].date.year
        month = administrative_expense[0].date.month
        days_in_month = calendar.monthrange(year, month)[1]

        # Get daily administrative expense
        expense = administrative_expense[0].administrative_expense / days_in_month

        # Grand total of administrative expense for active stores
        result = expense * active_stores[0].active_stores

        return result