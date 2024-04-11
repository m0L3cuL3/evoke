// Copyright (c) 2024, Sean Baang and contributors
// For license information, please see license.txt

frappe.query_reports["Daily Cash Flow Statement"] = {
	filters: [
		{
			fieldname: "daily_cash_flow_filter",
			label: "Daily Cash Flow",
			fieldtype: "Link",
			options: "Daily Cash Flow",
			reqd: 1,
		},
	],
	onload: function () {},
	formatter: function (value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);
		if (column.fieldname == "transaction") {
			if (value == "Income") {
				console.log(value);
				value = `<b style="color:limegreen">${value}</b>`;
			} else if (value == "Expenses") {
				console.log(value);
				value = `<p style="color:red">${value}</p>`;
			}
		}

		if (column.fieldname == "type") {
			if (value == "Sales") {
				console.log(value);
				value = `<b style="color:limegreen">${value}</b>`;
			} else {
				console.log(value);
				value = `<p style="color:red">${value}</p>`;
			}
		}

		return value;
	},
};
