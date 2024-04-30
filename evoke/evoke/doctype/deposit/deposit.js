// Copyright (c) 2024, Sean Baang and contributors
// For license information, please see license.txt

function updateTableRowStyle(frm, rows) {
	let partial_found = false;

	for (let i = 1; i < rows.length; i++) {
		rows[i].style.backgroundColor = ""; // Reset color for all rows
		const deposit = frm.doc.deposits[i - 1];

		if (deposit.accumulated_amount > 0 && !deposit.is_deposited) {
			rows[i].style.backgroundColor = "#a3222b";
		} else {
			rows[i].style.backgroundColor = "#173b2c";
		}
	}
}

frappe.ui.form.on("Deposit", {
	refresh: function (frm) {
		let deposits = frm.doc.deposits;
		let grand_total_amount = 0;
		let grand_total_accumulated_amount = 0;

		var rows = document.getElementsByClassName("grid-row");

		updateTableRowStyle(frm, rows);

		deposits.forEach((item) => {
			grand_total_amount += item.amount;
			grand_total_accumulated_amount += item.accumulated_amount;
		});

		frm.doc.grand_total_amount = grand_total_amount - grand_total_accumulated_amount;
		frm.doc.grand_total_accumulated_amount = grand_total_accumulated_amount;
		refresh_field("grand_total_amount");
		refresh_field("grand_total_accumulated_amount");
	},
	validate: function (frm) {
		let deposits = frm.doc.deposits;
		let grand_total_amount = 0;
		let grand_total_accumulated_amount = 0;

		var rows = document.getElementsByClassName("grid-row");

		updateTableRowStyle(frm, rows);

		deposits.forEach((item) => {
			grand_total_amount += item.amount;
			grand_total_accumulated_amount += item.accumulated_amount;
		});

		frm.doc.grand_total_amount = grand_total_amount - grand_total_accumulated_amount;
		frm.doc.grand_total_accumulated_amount = grand_total_accumulated_amount;
		refresh_field("grand_total_amount");
		refresh_field("grand_total_accumulated_amount");
	},
	cash_flow_entry: function (frm, cdt, cdn) {
		let cashflow = frm.doc.cash_flow_entry;

		frm.set_value("deposits", []);
		refresh_field("deposits");

		frappe.db.get_doc("Evoke Cash Flow", cashflow).then((doc) => {
			frm.doc.depository_date = frappe.datetime.add_days(doc.date, 1);
			frm.doc.transaction_date = doc.date;
			refresh_field("transaction_date");
			frappe
				.call({
					method: "evoke.utilities.api.get_deposits_per_store",
					args: {
						cash_flow_entry: cashflow,
						transaction_date: doc.date,
					},
					btn: $(".primary-action"),
					callback: (r) => {
						r.message.forEach((item) => {
							let entry = frm.add_child("deposits");
							entry.deposit_date = frm.doc.depository_date;
							entry.transaction_date = item.day_date;
							entry.store = item.store;
							entry.amount = item.deposit;
							// set default deposited status
							entry.is_deposited = 1;
						});
						refresh_field("deposits");
						refresh_field("depository_date");
					},
					error: (r) => {
						frappe.throw(__("Deposits failed to load."));
					},
				})
				.done((r) => {
					frappe.show_alert(
						{
							title: __("Depository"),
							indicator: "green",
							message: __(
								`Deposits loaded from <strong>${cashflow}</strong> successfully.`
							),
						},
						5
					);
				});
		});
	},
	depository_date: function (frm) {
		let cashflow = frm.doc.cash_flow_entry;
		frm.set_value("deposits", []);
		frappe.db.get_doc("Evoke Cash Flow", cashflow).then((doc) => {
			frm.doc.transaction_date = frappe.datetime.add_days(frm.doc.depository_date, -1);
			refresh_field("transaction_date");
			frappe
				.call({
					method: "evoke.utilities.api.get_deposits_per_store",
					args: {
						cash_flow_entry: cashflow,
						transaction_date: frm.doc.transaction_date,
					},
					btn: $(".primary-action"),
					callback: (r) => {
						r.message.forEach((item) => {
							let entry = frm.add_child("deposits");
							entry.deposit_date = frm.doc.depository_date;
							entry.transaction_date = item.day_date;
							entry.store = item.store;
							entry.amount = item.deposit;

							// set default deposited status
							entry.is_deposited = 1;
						});
						refresh_field("deposits");
						refresh_field("depository_date");
					},
				})
				.done((r) => {
					frappe.show_alert(
						{
							title: __("Depository"),
							indicator: "green",
							message: __(
								`Deposits loaded from <strong>${cashflow}</strong> successfully.`
							),
						},
						5
					);
				});
		});
	},
	transaction_date: function (frm) {
		let cashflow = frm.doc.cash_flow_entry;
		frm.set_value("deposits", []);
		frappe.db.get_doc("Evoke Cash Flow", cashflow).then((doc) => {
			frm.doc.depository_date = frappe.datetime.add_days(frm.doc.transaction_date, 1);
			frappe
				.call({
					method: "evoke.utilities.api.get_deposits_per_store",
					args: {
						cash_flow_entry: cashflow,
						transaction_date: frm.doc.transaction_date,
					},
					btn: $(".primary-action"),
					callback: (r) => {
						r.message.forEach((item) => {
							let entry = frm.add_child("deposits");

							entry.deposit_date = frm.doc.depository_date;
							entry.transaction_date = item.day_date;
							entry.store = item.store;
							entry.amount = item.deposit;

							// set default deposited status
							entry.is_deposited = 1;
						});
						refresh_field("deposits");
						refresh_field("depository_date");
					},
				})
				.done((r) => {
					frappe.show_alert(
						{
							title: __("Depository"),
							indicator: "green",
							message: __(
								`Deposits loaded from <strong>${cashflow}</strong> successfully.`
							),
						},
						5
					);
				});
		});
	},
});

frappe.ui.form.on("Credited Deposits", {
	refresh: function (frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		var rows = document.getElementsByClassName("grid-row");
		if (row.accumulated_amount > 0) {
			// change row style on update
			rows[row.idx].style.backgroundColor = "#a3222b";

			frm.get_field("deposits").grid.grid_rows[row.idx - 1].doc.accumulated_amount =
				row.accumulated_amount;
			frm.get_field("deposits").grid.grid_rows[row.idx - 1].doc.is_deposited = 0;

			frm.get_field("deposits").grid.grid_rows[row.idx - 1].refresh_field("is_deposited");
			frm.get_field("deposits").grid.grid_rows[row.idx - 1].refresh_field(
				"accumulated_amount"
			);
		} else {
			// change row style on update
			rows[row.idx].style.backgroundColor = "#173b2c";

			// update doc fields
			frm.get_field("deposits").grid.grid_rows[row.idx - 1].doc.accumulated_amount =
				row.accumulated_amount;
			frm.get_field("deposits").grid.grid_rows[row.idx - 1].doc.is_deposited = 1;

			// refresh fields
			frm.get_field("deposits").grid.grid_rows[row.idx - 1].refresh_field("is_deposited");
			frm.get_field("deposits").grid.grid_rows[row.idx - 1].refresh_field(
				"accumulated_amount"
			);
		}
	},
	accumulated_amount: function (frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		var rows = document.getElementsByClassName("grid-row");
		if (row.accumulated_amount > 0) {
			// change row style on update
			rows[row.idx].style.backgroundColor = "#a3222b";

			// update doc fields
			frm.get_field("deposits").grid.grid_rows[row.idx - 1].doc.accumulated_amount =
				row.accumulated_amount;
			frm.get_field("deposits").grid.grid_rows[row.idx - 1].doc.is_deposited = 0;

			// refresh fields
			frm.get_field("deposits").grid.grid_rows[row.idx - 1].refresh_field("is_deposited");
			frm.get_field("deposits").grid.grid_rows[row.idx - 1].refresh_field(
				"accumulated_amount"
			);
		} else {
			// change row style on update
			rows[row.idx].style.backgroundColor = "#173b2c";

			// update doc fields
			frm.get_field("deposits").grid.grid_rows[row.idx - 1].doc.accumulated_amount =
				row.accumulated_amount;
			frm.get_field("deposits").grid.grid_rows[row.idx - 1].doc.is_deposited = 1;

			// refresh fields
			frm.get_field("deposits").grid.grid_rows[row.idx - 1].refresh_field("is_deposited");
			frm.get_field("deposits").grid.grid_rows[row.idx - 1].refresh_field(
				"accumulated_amount"
			);
		}
	},
});
