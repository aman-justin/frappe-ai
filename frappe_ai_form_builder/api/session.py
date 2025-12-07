"""Session API for AI Form Builder - Interview Demo"""
import frappe
from frappe import _
import json
from datetime import datetime

@frappe.whitelist(allow_guest=True)
def start_session(template=None):
    """Start conversation"""
    conv = frappe.get_doc({
        "doctype": "AI Conversation",
        "user": frappe.session.user,
        "template": template or "custom",
        "state": "active",
        "conversation_history": "[]",
        "created_at": datetime.now()
    })
    conv.insert()
    frappe.db.commit()
    
    msg = "Hi! What form do you want to create? Tell me what fields you need."
    return {"session_id": conv.name, "message": msg}

@frappe.whitelist(allow_guest=True)
def send_message(session_id, message):
    """Send message and get AI response"""
    try:
        # Get conversation
        conversation = frappe.get_doc("AI Conversation", session_id)
        history = json.loads(conversation.conversation_history or "[]")
        
        # Get AI response using real LLM
        from frappe_ai_form_builder.api.llm_adapter import get_llm_response
        ai_response = get_llm_response(history, message)
        
        # Add user message to history
        history.append({"role": "user", "content": message})
        
        # Add AI response to history
        history.append({"role": "assistant", "content": ai_response["message"]})
        
        # Save draft spec if provided
        if ai_response.get("draft_spec"):
            conversation.draft_specification = json.dumps(ai_response["draft_spec"])
        
        # Update conversation
        conversation.conversation_history = json.dumps(history)
        conversation.save(ignore_permissions=True)
        frappe.db.commit()
        
        return {
            "message": ai_response["message"],
            "ready_to_generate": ai_response.get("ready_to_generate", False),
            "draft_spec": ai_response.get("draft_spec")
        }
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Send Message Error")
        frappe.throw(_("Failed to send message: {0}").format(str(e)))

@frappe.whitelist(allow_guest=True)
def generate_doctype(session_id, publish=True):
    """Generate DocType using real generator"""
    try:
        # Use the real generator you already have!
        from frappe_ai_form_builder.api.generator import generate_doctype as gen_doctype
        result = gen_doctype(session_id, publish)
        return result
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Generate DocType Error")
        frappe.throw(_("Failed to generate DocType: {0}").format(str(e)))
