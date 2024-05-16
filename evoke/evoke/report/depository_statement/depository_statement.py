# Copyright (c) 2024, Sean Baang and contributors
# For license information, please see license.txt

import frappe

def execute(filters=None):
	data = get_data(filters)
	columns = get_columns()
	tree_data = format_as_tree(data)
	return columns, tree_data

def get_filters(filters):
	if filters.get('date_from') and filters.get('date_to'):
		return [['deposit_date', 'between', [filters.get('date_from'), filters.get('date_to')]]]

def get_columns():
	columns = [
		{ 'fieldname': 'store', 'label': 'Store', 'width': 150 },
		{ 'fieldname': 'depository_date', 'label': 'Depository Date', 'width': 125 },
		{ 'fieldname': 'transaction_date', 'label': 'Transaction Date', 'width': 125 },
		{ 'fieldname': 'over_short_amount', 'label': 'Over / Short', 'fieldtype': 'Currency', 'width': 100 },
		{ 'fieldname': 'for_deposit_amount', 'fieldtype': 'Currency', 'label': 'For Deposit', 'width': 150 },
		{ 'fieldname': 'amount_credited', 'fieldtype': 'Currency', 'label': 'Amount Credited to Account', 'width': 140 },
		{ 'fieldname': 'is_deposited', 'label': 'Is Deposited', 'align': 'center', 'width': 140 }
	]

	return columns

def get_data(filters):
	filter = get_filters(filters)
	deposits = frappe.db.get_all(
		'Deposit', 
		fields=[
			'deposits.store',
			'deposits.transaction_date', 
			'deposits.deposit_date',
			'deposits.over_short_amount',
			'deposits.for_deposit_amount', 
			'deposits.amount_credited',
			'deposits.is_deposited'
		], 
		filters=filter,
		order_by='store asc, depository_date desc'
	)

	data = {}
	for row in deposits:
		store = row['store']
		if store not in data:
			data[store] = []
		
		data[store].append({
			# 'store': store, 
			'depository_date': row['deposit_date'], 
			'transaction_date': row['transaction_date'],
			'over_short_amount': row['over_short_amount'],
			'for_deposit_amount': row['for_deposit_amount'],
			'amount_credited': row['amount_credited'],
			'is_deposited': 'Yes' if row['is_deposited'] == 1 else 'No'
		})

	return data

def format_as_tree(data):
	tree_data = []
	for store, deposits in data.items():
		tree_data.append({
			'store': store,
			'depository_date': '',
			'transaction_date': '',
			'over_short_amount': sum(depo['over_short_amount'] for depo in deposits),
			'for_deposit_amount': sum(depo['for_deposit_amount'] for depo in deposits),
			'amount_credited': sum(depo['amount_credited'] for depo in deposits),
			'is_deposited': '',
			'indent': 0,
			'has_children': 1
		})

		for deposit in deposits:
			deposit['indent'] = 1
			tree_data.append(deposit)
	return tree_data