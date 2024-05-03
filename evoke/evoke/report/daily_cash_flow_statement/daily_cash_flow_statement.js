// Copyright (c) 2024, Sean Baang and contributors
// For license information, please see license.txt

frappe.query_reports["Daily Cash Flow Statement"] = {
	filters: [
		{
			fieldname: "date_from",
			label: "Date From",
			fieldtype: "Date",
			reqd: 1,
		},
		{
			fieldname: "date_to",
			label: "Date To",
			fieldtype: "Date",
			reqd: 1,
		},
	],
	onload: function (report) {
		report.page.add_inner_button(
			__("Profit and Loss Statement"),
			function () {
				var filters = report.get_values();
				frappe.set_route("query-report", "Profit and Loss Statement", {
					date_from: filters.date_from,
					date_to: filters.date_to,
				});
			},
			"Reports"
		);
		report.page.add_inner_button(
			__("Depository Statement"),
			function () {
				var filters = report.get_values();
				frappe.set_route("query-report", "Depository Statement", {
					date_from: filters.date_from,
					date_to: filters.date_to,
				});
			},
			"Reports"
		);
	},
	formatter: function (value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);
		if (column.fieldname == "transaction") {
			if (value == "Income") {
				value = `<b style="color:limegreen">${value}</b>`;
			} else if (value == "Expenses") {
				value = `<p style="color:red">${value}</p>`;
			}
		}

		if (column.fieldname == "type") {
			if (value == "Sales") {
				value = `<b style="color:limegreen">${value}</b>`;
			} else {
				value = `<p style="color:red">${value}</p>`;
			}
		}

		return value;
	},
};
