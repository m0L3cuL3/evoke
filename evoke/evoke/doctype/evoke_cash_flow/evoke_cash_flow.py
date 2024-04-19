# Copyright (c) 2024, Sean Baang and contributors
# For license information, please see license.txt

from datetime import datetime, timedelta
import frappe
from frappe.model.document import Document


class EvokeCashFlow(Document):
	def validate(self):
		pass
		# self.set_month_year()

	# def set_month_year(self):
	# 	# Convert input string to datetime object
	# 	date = self.date
	# 	input_datetime = datetime.strptime(date, "%Y-%m-%d")
		
	#  	# Extract month and year from the input date and format them
	# 	month = input_datetime.strftime("%B")  # Get full month name
	# 	year = input_datetime.year
	# 	self.month_year_entry = f"{month} {year}"

	# def before_save(self):
	# 	self.set_doc_name()

	# def set_doc_name(self):
	# 	# Convert input string to datetime object
	# 	date = self.date
	# 	input_datetime = datetime.strptime(date, "%Y-%m-%d")
		
	# 	# Extract month and year from the input date and format them
	# 	month = input_datetime.strftime("%B")  # Get full month name
	# 	year = input_datetime.year
	# 	self.month_year_entry
	# 	self.name = f"{month} {year}"
