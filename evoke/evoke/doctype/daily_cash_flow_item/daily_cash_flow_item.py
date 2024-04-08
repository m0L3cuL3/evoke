# Copyright (c) 2024, Sean Baang and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class DailyCashFlowItem(Document):
	def validate(self):
		pass

	def before_save(self):
		pass
