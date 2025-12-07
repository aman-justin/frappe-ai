import frappe

def check_ai_doctypes():
    try:
        doctypes = frappe.db.get_all('DocType', 
            filters={'module': ['in', ['ai_audit_log', 'ai_config', 'ai_conversation', 'ai_generated_artifact']]},
            fields=['name', 'module'])
        
        print("AI DocTypes found:")
        for d in doctypes:
            print(f"  - {d.name} ({d.module})")
        
        if not doctypes:
            print("  No AI DocTypes found")
            
        return len(doctypes)
    except Exception as e:
        print(f"Error checking DocTypes: {e}")
        return 0

check_ai_doctypes()
