// Copyright (c) 2024, Sean Baang and contributors
// For license information, please see license.txt

frappe.ui.form.on("Store Rental Rates", {
	rental_date: function (frm, cdt, cdn) {
		var child = locals[cdt][cdn];
		frappe
			.call({
				method: "evoke.api.get_month_and_year",
				args: { date: child.rental_date },
			})
			.done((r) => {
				child.rental_month_year = r.message;
				refresh_field("store_rental_rates");
			});
	},
});
