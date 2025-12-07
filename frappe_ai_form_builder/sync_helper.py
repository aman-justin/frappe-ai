import frappe
from frappe.model.sync import sync_for


def sync_app():
    print('Running sync for frappe_ai_form_builder...')
    try:
        sync_for('frappe_ai_form_builder', force=True, reset_permissions=True)
        print('Done sync')
    except Exception as e:
        print('Sync error:', e)
