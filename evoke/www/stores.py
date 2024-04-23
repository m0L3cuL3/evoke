import frappe

def get_context(context):
    ## load some data and put it in context
    context.no_cache = 1
    context.show_sidebar = True
    context.title = 'Stores'
    context.stores = frappe.db.get_all("Store", fields=['*'])