# Copyright (c) 2024, Sean Baang and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Deposit(Document):
	def validate(self):
		self.set_status()
		self.check_amount_found()

	def check_amount_found(self):
		row = None

		for d in self.get('deposits'):
			if d.amount_credited or d.accumulated_amount:
				pass
			else:
				row = d.idx
				break

		if row is not None:
			frappe.throw('Amount not found in row #{}'.format(row))
				


	def set_status(self):
		partial_found = False
    
		for d in self.get('deposits'):
			if d.accumulated_amount and d.accumulated_amount > 0 and not d.is_deposited:
				partial_found = True
				d.is_deposited = 0
				break  # Stop iterating once 'Partial' status is found
			else:
				d.is_deposited = 1

				
		if partial_found:
			self.status = 'Partial'
		else:
			self.status = 'Completed'
