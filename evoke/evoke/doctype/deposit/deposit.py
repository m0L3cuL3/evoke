# Copyright (c) 2024, Sean Baang and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Deposit(Document):
	def validate(self):
		self.set_status()

	def set_status(self):
		for d in self.get('deposits'):
			if d.over_short_amount == 0 and d.amount_credited == d.for_deposit_amount:
				d.is_deposited = 1
				d.is_short = 0

			if  d.over_short_amount < 0 and d.amount_credited == 0:
				d.is_deposited = 0
				d.is_short = 1

			if d.over_short_amount < 0 and d.amount_credited > 0:
				d.is_deposited = 1
				d.is_short = 1
			
			if d.over_short_amount > 0 and d.amount_credited > 0:
				d.is_deposited = 1
				d.is_short = 0
				
		if self.total_for_deposit_amount == self.total_amount_credited:
			self.status = 'Completed'
		else:
			self.status = 'Partial'