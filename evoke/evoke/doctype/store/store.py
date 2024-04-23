# Copyright (c) 2024, Sean Baang and contributors
# For license information, please see license.txt

import frappe
from frappe.website.website_generator import WebsiteGenerator


class Store(WebsiteGenerator):
	def validate(self):
		if not self.route:
			self.route = "stores/" + self.name.lower().replace(" ", "-")

	def get_context(self, context):
		context.no_cache = 1
		context.title = self.name
		context.parents = [
			{
				'name': 'Stores',
				'title': 'Stores',
				'route': 'stores'
			}
		]
	
	website = frappe._dict(
			template="templates/generators/store_info.html",
			page_title_field="name"
		)
