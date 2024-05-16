frappe.query_reports["Profit and Loss Statement"] = {
	filters: [
		{
			fieldname: "evoke_date_select_filter",
			label: "Date Filter Type",
			fieldtype: "Select",
			options: ["", "Today", "Yesterday", "Past 7 Days", "Past 30 Days", "Date Range"],
			default: 0,
			on_change: function (query_report) {
				switch (frappe.query_report.get_filter_value("evoke_date_select_filter")) {
					case "":
						query_report.set_filter_value("evoke_date_from", "");
						query_report.set_filter_value("evoke_date_to", "");
						break;
					case "Today":
						query_report.set_filter_value(
							"evoke_date_from",
							frappe.datetime.get_today()
						);
						query_report.set_filter_value(
							"evoke_date_to",
							frappe.datetime.get_today()
						);
						break;
					case "Yesterday":
						query_report.set_filter_value(
							"evoke_date_from",
							frappe.datetime.add_days(frappe.datetime.get_today(), -1)
						);
						query_report.set_filter_value(
							"evoke_date_to",
							frappe.datetime.add_days(frappe.datetime.get_today(), -1)
						);
						break;
					case "Past 7 Days":
						query_report.set_filter_value(
							"evoke_date_from",
							frappe.datetime.add_days(frappe.datetime.get_today(), -7)
						);
						query_report.set_filter_value(
							"evoke_date_to",
							frappe.datetime.get_today()
						);
						break;
					case "Past 30 Days":
						query_report.set_filter_value(
							"evoke_date_from",
							frappe.datetime.add_days(frappe.datetime.get_today(), -30)
						);
						query_report.set_filter_value(
							"evoke_date_to",
							frappe.datetime.get_today()
						);
						break;
					case "Date Range":
						query_report.set_filter_value("evoke_date_from", "");
						query_report.set_filter_value("evoke_date_to", "");
						break;
					default:
						query_report.set_filter_value("evoke_date_from", "");
						query_report.set_filter_value("evoke_date_to", "");
						break;
				}

				query_report.refresh();
			},
		},
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
	get_datatable_options(options) {
		console.log(options);
		// Modify DataTable options here if needed
		options.sticky = {
			headers: true,
			columns: 2, // Number of columns to freeze
		};
		return options;
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

		if (column.fieldname == "sales") {
			value = `<b style="color:limegreen">${value}</b>`;
		}

		if (column.fieldname == "expenses") {
			value = `<b style="color:red">${value}</b>`;
		}

		return value;
	},
};
