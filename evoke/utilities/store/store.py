import frappe
from datetime import datetime

class StoreUtils:
    # Applies monthly rental rates of store
    # Returns float number
    def apply_monthly_rental_rates(store_name, initial_date):
        store_rental_rates = frappe.db.get_all(
            "Store", 
            fields=[
                'store_name', 
                'store_rental_rates.rental_date', 
                'store_rental_rates.rental_rate'
            ], 
            filters=[
                ['store_name', '=', store_name]
            ]
        )
        for rate_obj in reversed(store_rental_rates):
            rental_date = rate_obj['rental_date']
            if rental_date is not None:
                if isinstance(rental_date, str):
                    rental_date = datetime.strptime(rental_date, "%Y-%m-%d").date()  # Convert rental_date to datetime object
                if initial_date >= rental_date:
                    return rate_obj['rental_rate']
        return None  # Return None if no matching rate is found