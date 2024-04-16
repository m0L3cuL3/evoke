frappe.query_reports["Profit and Loss Statement"] = {
	filters: [
		{
			fieldname: "evoke_cash_flow_filter",
			label: "Evoke Cash Flow",
			fieldtype: "Link",
			options: "Evoke Cash Flow",
			reqd: 1,
		},
	],
	onload: function (report) {
		report.page.add_inner_button(
			__("Daily Cash Flow Statement"),
			function () {
				var filters = report.get_values();
				frappe.set_route("query-report", "Daily Cash Flow Statement", {
					evoke_cash_flow_filter: filters.evoke_cash_flow_filter,
				});
			},
			"Reports"
		);
	},
	formatter: function (value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);
		if (column.fieldname == "profit_loss") {
			if (data["profit_loss"] > 0) {
				value = `<b style="color:limegreen">${value}</b>`;
			}
		}

		if (column.fieldname == "profit_loss") {
			if (data["profit_loss"] < 0) {
				value = `<b style="color:red">${value}</b>`;
			}
		}

		return value;
	},
};
