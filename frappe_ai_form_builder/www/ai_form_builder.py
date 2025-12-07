import frappe

def get_context(context):
    """Web page context"""
    context.no_cache = 1
    context.show_sidebar = False
    
    # Pass CSRF token to template (allow Guest for demo)
    context.csrf_token = frappe.sessions.get_csrf_token()
    
    return context
