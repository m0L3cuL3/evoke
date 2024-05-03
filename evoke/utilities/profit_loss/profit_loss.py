import frappe
import calendar

class ProfitLossUtils:
    def get_total_of_transaction_type(store, type, transaction, filters):
        data = frappe.db.get_all(
            'Evoke Cash Flow',
            fields=[
                'daily_entries.amount',
                'sum(amount) as total_amount'
            ],
            filters=[
                ['store', '=', store],
                ['type', '=', type],
                ['transaction', '=', transaction],
                ['day_date', 'between', [filters.get('date_from'), filters.get('date_to')]]
            ]
        )

        result = data[0].total_amount

        if result == None:
            result = 0

        return result
    
    def get_administrative_expenses_per_store(filters):
        administrative_expense = frappe.db.get_all(
            'Evoke Cash Flow',
            fields=[
                'administrative_expense',
                'date'
            ],
            filters=[
                ['day_date', 'between', [filters.get('date_from'), filters.get('date_to')]]
            ]
        )

        if administrative_expense:
            year = administrative_expense[0].date.year
            month = administrative_expense[0].date.month
            days_in_month = calendar.monthrange(year, month)[1]

            return administrative_expense[0].administrative_expense / days_in_month
        else:
            return 0


    def get_operational_expenses(filters):
        operating_expense_result = frappe.db.get_all(
            'Evoke Cash Flow',
            fields=[
                'daily_entries.amount',
                'sum(amount) as operating_expenses_amount'
            ],
            filters=[
                ['day_date', 'between', [filters.get('date_from'), filters.get('date_to')]],
                ['store', '=', 'Office / Warehouse'],
                ['type', '=', 'Operating Expenses'],
                ['transaction', '=', 'Expenses']
            ]
        )

        active_stores_result = frappe.db.get_all(
            'Store',
            fields=[
                'count(store_name) as active_stores'
            ],
            filters=[
                ['is_active', '=', True]
            ]
        )

        operating_expense = operating_expense_result[0].operating_expenses_amount
        active_stores = active_stores_result[0].active_stores

        if operating_expense == None:
            operational_expenses = 0
        else:
            operational_expenses = operating_expense / active_stores
        
        return operational_expenses