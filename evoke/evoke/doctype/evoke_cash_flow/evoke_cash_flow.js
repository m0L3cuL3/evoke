// Copyright (c) 2024, Sean Baang and contributors
// For license information, please see license.txt

frappe.ui.form.on("Evoke Cash Flow", {
	refresh: function (frm) {
		frm.set_df_property("date", "read_only", frm.is_new() ? 0 : 1);
	},
	date: function (frm) {
		let date = frm.doc.date;
		if (date && frm.doc.__islocal) {
			frappe
				.call({
					method: "evoke.utilities.api.get_days_of_month",
					args: { date: date },
				})
				.done((r) => {
					frm.doc.daily_entries = [];
					$.each(r.message, function (i, e) {
						let entry = frm.add_child("daily_entries");
						entry.day_date = e;
					});
					refresh_field("daily_entries");
				});
			frappe
				.call({
					method: "evoke.utilities.api.get_month_and_year",
					args: { date: date },
				})
				.done((r) => {
					frm.doc.month_year_entry = r.message;
					refresh_field("month_year_entry");
				});
		}
	},
});

frappe.ui.form.on("Daily Cash Flow Item", {
	onload: function (frm) {},
	refresh: function (frm) {
		frm.fields_dict.transaction.$input.on("change", function () {
			var selectedOption = $(this).val();
			if (selectedOption === "Income") {
				$(this).css("color", "var(--yellow-600)");
			} else if (selectedOption === "Expenses") {
				$(this).css("color", "var(--blue-600)");
			}
		});
	},
	transaction: function (frm) {
		// frappe.meta.docfield_map["Select"].fieldtype.formatter = (value) => {
		// 	console.log(value);
		// 	if (value === "Income") return "🔵 Section Break";
		// 	else return value;
		// };
	},
});
