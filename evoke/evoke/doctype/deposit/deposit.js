// Copyright (c) 2024, Sean Baang and contributors
// For license information, please see license.txt

function updateTableRowStyle(frm, rows) {
	for (let i = 1; i < rows.length; i++) {
		const deposit = frm.doc.deposits[i - 1];

		// if (deposit.is_deposited && !deposit.is_short) {
		// 	console.log("deposited");
		// 	rows[i].style.backgroundColor = "#173b2c"; // green
		// } else if (deposit.is_deposited && deposit.is_short) {
		// 	console.log("deposited but short");
		// 	rows[i].style.backgroundColor = "#a3222b"; // red
		// } else if (!deposit.is_deposited && deposit.is_short) {
		// 	console.log("did not deposit");
		// 	rows[i].style.backgroundColor = "#a3222b"; // red
		// } else {
		// 	rows[i].style.backgroundColor = "";
		// }

		if (deposit.over_short_amount < 0) {
			rows[i].style.backgroundColor = "#a3222b";
		} else {
			rows[i].style.backgroundColor = "#173b2c";
		}

		if (deposit.amount_credited == 0) {
			rows[i].style.backgroundColor = "#a3222b";
		}
	}
}

function updateGrandTotal(frm) {
	let deposits = frm.doc.deposits;
	let total_for_deposit_amount = 0;
	let total_amount_credited = 0;

	deposits.forEach((item) => {
		total_for_deposit_amount += item.for_deposit_amount;
		total_amount_credited += item.amount_credited;
	});

	frm.doc.total_for_deposit_amount = total_for_deposit_amount;
	frm.doc.total_amount_credited = total_amount_credited;

	refresh_field("total_for_deposit_amount");
	refresh_field("total_amount_credited");
}

function generateDepositBreakdownContent(data) {
	var content = ``;

	data.forEach(function (item) {
		const isDeposited =
			item.is_deposited && !item.is_short
				? {}
				: {
						fieldtype: "Currency",
						options: "currency",
				  };
		content += `<p class="m-0">[${moment(item.deposit_date).format(
			"dddd, MMMM Do YYYY"
		)}]: <strong>${frappe.format(item.amount, isDeposited, { inline: true })}</strong></p>`;
	});
	return content;
}

function getAccumulatedDeposits(frm) {
	frappe
		.call({
			method: "evoke.utilities.api.get_accumulated_deposits",
			error: (r) => {
				frappe.throw(__("Deposits failed to load."));
			},
		})
		.done((r) => {
			// Convert date strings to Date objects
			let depositories = r.message;
			const depository_date = new Date(frm.doc.depository_date);
			depositories.forEach((depo) => {
				depo["deposit_date"] = new Date(depo["deposit_date"]);
				depo["transaction_date"] = new Date(depo["transaction_date"]);
			});

			// Group non-deposited transactions by store
			let nonDepositedByStore = {};
			depositories.forEach((depo) => {
				if (!nonDepositedByStore[depo["store"]]) {
					nonDepositedByStore[depo["store"]] = [];
				}
				nonDepositedByStore[depo["store"]].push({
					amount:
						depo["is_deposited"] && !depo["is_short"]
							? "Deposited"
							: depo["over_short_amount"],
					deposit_date: depo["deposit_date"].toISOString().split("T")[0],
					is_deposited: depo["is_deposited"],
					is_short: depo["is_short"],
				});
			});

			// Print the breakdown by store
			Object.entries(nonDepositedByStore).forEach(([store, data]) => {
				frm.fields_dict["deposits"].$wrapper
					.find(".grid-body .rows")
					.find(".grid-row")
					.each(function (i, item) {
						let d =
							locals[frm.fields_dict["deposits"].grid.doctype][
								$(item).attr("data-name")
							];

						let forDepositCell = $(item).find("[data-fieldname='for_deposit_amount']");

						if (d["store"] == store) {
							forDepositCell.popover({
								title: store,
								html: true,
								placement: "left",
								trigger: "hover focus",
								content: function () {
									return generateDepositBreakdownContent(data);
								},
							});
						}
					});
			});
		});
}

frappe.ui.form.on("Deposit", {
	refresh: function (frm) {
		var rows = document.getElementsByClassName("grid-row");
		frm.set_df_property("deposits", "cannot_add_rows", true);
		getAccumulatedDeposits(frm);

		updateTableRowStyle(frm, rows);
		updateGrandTotal(frm);
	},
	validate: function (frm) {
		var rows = document.getElementsByClassName("grid-row");

		updateTableRowStyle(frm, rows);
		updateGrandTotal(frm);
	},
	depository_date: function (frm) {
		frm.set_value("deposits", []);
		frm.doc.transaction_date = frappe.datetime.add_days(frm.doc.depository_date, -1);
		refresh_field("transaction_date");
		frappe
			.call({
				method: "evoke.utilities.api.get_deposits_per_store",
				args: {
					transaction_date: frm.doc.transaction_date,
				},
				btn: $(".primary-action"),
				callback: (r) => {
					r.message.forEach((item) => {
						let entry = frm.add_child("deposits");
						entry.deposit_date = frm.doc.depository_date;
						entry.transaction_date = item.day_date;
						entry.store = item.store;
						entry.for_deposit_amount = item.for_deposit_amount;
						entry.over_short_amount = item.over_short_amount;

						if (item.for_deposit_amount > entry.for_deposit_amount) {
							entry.for_deposit_amount =
								item.for_deposit_amount - item.over_short_amount;
						} else if (item.for_deposit_amount < entry.for_deposit_amount) {
							entry.for_deposit_amount =
								item.for_deposit_amount + Math.abs(item.over_short_amount);
						} else if (item.for_deposit_amount == entry.for_deposit_amount) {
							entry.for_deposit_amount = item.for_deposit_amount;
						}
					});
					refresh_field("deposits");
					refresh_field("depository_date");
				},
			})
			.done((r) => {
				const transaction_date = moment(frm.doc.transaction_date).format(
					"dddd, MMMM Do YYYY"
				);
				const indicator = r.message.length > 0 ? "green" : "red";
				const message =
					r.message.length > 0
						? `Successfully loaded transactions from ${transaction_date}.`
						: `No transactions found from ${transaction_date}.`;

				frappe.show_alert(
					{
						title: __("Depository"),
						indicator: indicator,
						message: __(message),
					},
					5
				);
			});
	},
});

frappe.ui.form.on("Credited Deposits", {
	refresh: function (frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		var rows = document.getElementsByClassName("grid-row");
		const depositField = frm.get_field("deposits").grid.grid_rows[row.idx - 1];

		if (row.over_short_amount < 0) {
			rows[row.idx].style.backgroundColor = "#a3222b";
		} else {
			rows[row.idx].style.backgroundColor = "#173b2c";
		}

		row.over_short_amount = row.amount_credited - row.for_deposit_amount;

		depositField.refresh_field("is_short");
		depositField.refresh_field("is_deposited");
		depositField.refresh_field("over_short_amount");
	},
	amount_credited: function (frm, cdt, cdn) {
		const row = locals[cdt][cdn];
		var rows = document.getElementsByClassName("grid-row");
		const depositField = frm.get_field("deposits").grid.grid_rows[row.idx - 1];

		console.log(row);

		if (
			row.amount_credited > row.for_deposit_amount ||
			row.amount_credited == row.for_deposit_amount
		) {
			rows[row.idx].style.backgroundColor = "#173b2c";
		} else {
			rows[row.idx].style.backgroundColor = "#a3222b";
		}

		row.over_short_amount = row.amount_credited - row.for_deposit_amount;

		depositField.refresh_field("is_short");
		depositField.refresh_field("is_deposited");
		depositField.refresh_field("over_short_amount");
	},
});
