// Copyright (c) 2024, Sean Baang and contributors
// For license information, please see license.txt

frappe.query_reports['Daily Cash Flow Statement'] = {
  filters: [
    {
      fieldname: 'daily_cash_flow_filter',
      label: 'Daily Cash Flow',
      fieldtype: 'Link',
      options: 'Daily Cash Flow',
      reqd: 1,
    },
  ],
};
