# Copyright (c) 2024, Sean Baang and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class CreditedDeposits(Document):
	def validate(self):
		self.check_deposit()
	
	def check_deposit(self):
		if self.amount > 0:
			self.is_deposited = 1
		else:
			self.is_deposited = 0