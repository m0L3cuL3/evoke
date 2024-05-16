// Copyright (c) 2024, Sean Baang and contributors
// For license information, please see license.txt

frappe.ui.form.on("Evoke Cash Flow", {
	refresh: function (frm) {
		frm.set_df_property("date", "read_only", frm.is_new() ? 0 : 1);
		// frm.set_df_property("daily_entries", "cannot_add_rows", true);
		frm.fields_dict["daily_entries"].$wrapper
			.find(".grid-body .rows")
			.find(".grid-row")
			.each(function (i, item) {
				let d =
					locals[frm.fields_dict["daily_entries"].grid.doctype][
						$(item).attr("data-name")
					];

				let transactionCell = $(item).find("[data-fieldname='transaction']");

				if (d["transaction"] == "Income") {
					transactionCell.css({ color: "limegreen" });
				} else {
					transactionCell.css({ color: "red" });
				}
			});
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
	add_single_row: function (frm) {
		frm.add_child("daily_entries");
		refresh_field("daily_entries");
	},
});

frappe.ui.form.on("Daily Cash Flow Item", {
	refresh: function (frm) {},
	transaction: function (frm, cdt, cdn) {
		frm.fields_dict["daily_entries"].$wrapper
			.find(".grid-body .rows")
			.find(".grid-row")
			.each(function (i, item) {
				let d =
					locals[frm.fields_dict["daily_entries"].grid.doctype][
						$(item).attr("data-name")
					];

				let transactionCell = $(item).find("[data-fieldname='transaction']");

				if (d["transaction"] == "Income") {
					transactionCell.css({ color: "limegreen" });
				} else {
					transactionCell.css({ color: "red" });
				}
			});
	},
});
