# Copyright (c) 2024, Sean Baang and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
	data = get_data()
	columns = get_columns()
	return columns, data

def get_columns():
	columns = [
		{ 'fieldname': 'cash_flow_entry', 'label': 'Cash Flow Entry', 'width': 150 },
		{ 'fieldname': 'store', 'label': 'Store', 'width': 150 },
		{ 'fieldname': 'depository_date', 'label': 'Depository Date', 'width': 150 },
		{ 'fieldname': 'transaction_date', 'label': 'Transaction Date', 'width': 150 },
		{ 'fieldname': 'over_short_amount', 'label': 'Over / Short', 'fieldtype': 'Currency', 'width': 150 },
		{ 'fieldname': 'for_deposit_amount', 'fieldtype': 'Currency', 'label': 'For Deposit', 'width': 150 },
		{ 'fieldname': 'amount_credited', 'fieldtype': 'Currency', 'label': 'Amount Credited to Account', 'width': 150 },
		{ 'fieldname': 'accumulated_amount', 'fieldtype': 'Currency', 'label': 'Accumulated Amount', 'width': 150 },
		{ 'fieldname': 'is_deposited', 'label': 'Is Deposited', 'align': 'center', 'width': 150 }
	]

	return columns

def get_data():
	data = []
	deposits = frappe.db.get_all(
		'Deposit', 
		fields=[
			'cash_flow_entry', 
			'deposits.store', 
			'deposits.deposit_date', 
			'deposits.transaction_date', 
			'deposits.over_short_amount',
			'deposits.for_deposit_amount', 
			'deposits.amount_credited',
			'deposits.accumulated_amount',
			'deposits.is_deposited'
			], 
			filters=[],
			order_by='deposit_date desc, store desc'
		)

	for row in deposits:

		if row['is_deposited'] == 1:
			data.append({
				'cash_flow_entry': row['cash_flow_entry'], 
				'store': row['store'], 
				'depository_date': row['deposit_date'], 
				'transaction_date': row['transaction_date'],
				'over_short_amount': row['over_short_amount'],
				'for_deposit_amount': row['for_deposit_amount'],
				'amount_credited': row['amount_credited'],
				'accumulated_amount': row['accumulated_amount'],
				'is_deposited': 'Yes'
			})
		else: 
			data.append({
				'cash_flow_entry': row['cash_flow_entry'], 
				'store': row['store'], 
				'depository_date': row['deposit_date'], 
				'transaction_date': row['transaction_date'],
				'over_short_amount': row['over_short_amount'],
				'for_deposit_amount': row['for_deposit_amount'],
				'amount_credited': row['amount_credited'],
				'accumulated_amount': row['accumulated_amount'],
				'is_deposited': 'No'
			})
			

		

	return data