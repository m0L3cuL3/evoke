// Copyright (c) 2024, Sean Baang and contributors
// For license information, please see license.txt

frappe.query_reports["Depository Statement"] = {
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
			__("Daily Cash Flow Statement"),
			function () {
				var filters = report.get_values();
				frappe.set_route("query-report", "Daily Cash Flow Statement", {
					date_from: filters.date_from,
					date_to: filters.date_to,
				});
			},
			"Reports"
		);
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
	},
	formatter: function (value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);
		if (column.fieldname == "is_deposited") {
			if (value == "Yes") {
				value = `<b style="color:#13ad68">${value}</b>`;
			} else {
				value = `<b style="color:#eb4034">${value}</b>`;
			}
		}

		if (column.fieldname == "over_short_amount") {
			if (data["over_short_amount"] > 0) {
				value = `<b style="color:#13ad68">${value}</b>`;
			} else if (data["over_short_amount"] < 0) {
				value = `<b style="color:#eb4034">${value}</b>`;
			}
		}

		if (column.fieldname == "for_deposit_amount") {
			if (data["for_deposit_amount"] > 0) {
				value = `<b style="color:#1374eb">${value}</b>`;
			}
		}

		if (column.fieldname == "amount_credited") {
			if (data["amount_credited"] >= 0) {
				value = `<b style="color:#13ad68">${value}</b>`;
			}
		}

		if (column.fieldname == "accumulated_amount") {
			if (data["accumulated_amount"] > 0) {
				value = `<b style="color:#eb4034">${value}</b>`;
			}
		}

		return value;
	},
	tree: true,
	name_field: "depository",
	parent_field: "parent_depository",
	initial_depth: 3,
};
