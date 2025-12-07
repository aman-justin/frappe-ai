"""DocType Generator - Creates Frappe DocTypes from AI specifications"""

import frappe
from frappe import _
import json


@frappe.whitelist(allow_guest=True)
def generate_doctype(session_id, publish=False):
    """
    Generate a DocType from AI conversation specification.
    
    Args:
        session_id (str): The conversation session ID
        publish (bool): If True, create active DocType. If False, save as draft.
    
    Returns:
        dict: Generated artifact details
    """
    try:
        # Get conversation and draft specification
        conversation = frappe.get_doc("AI Conversation", session_id)
        
        if not conversation.draft_specification:
            frappe.throw(_("No draft specification found. Continue the conversation to generate a form."))
        
        spec = json.loads(conversation.draft_specification)
        
        # Validate specification
        from frappe_ai_form_builder.api.llm_adapter import validate_doctype_spec
        validation_errors = validate_doctype_spec(spec)
        
        if validation_errors:
            frappe.throw(_("Specification validation failed:\n{0}").format("\n".join(validation_errors)))
        
        # Create AI Generated Artifact record
        doctype_name = spec.get("doctype_name") or spec.get("name")
        artifact = frappe.get_doc({
            "doctype": "AI Generated Artifact",
            "artifact_type": "DocType",
            "artifact_name": doctype_name,
            "content": json.dumps(spec),
            "status": "approved" if publish else "draft",
            "session_id": session_id,
            "created_by": frappe.session.user
        })
        artifact.insert()
        
        # If publish is True, create the actual DocType
        if publish:
            created_doctype = create_doctype_from_spec(spec, artifact.name)
            artifact.frappe_doctype = created_doctype.name
            artifact.save()
        
        frappe.db.commit()
        
        # Log audit trail
        doctype_name = spec.get("doctype_name") or spec.get("name")
        log_audit_action("generate", artifact.name, doctype_name)
        
        return {
            "artifact_id": artifact.name,
            "doctype_name": spec.get("doctype_name") or spec.get("name"),
            "module": spec.get("module"),
            "status": artifact.status,
            "message": _("DocType generated successfully") if publish else _("Draft saved for admin review")
        }
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "AI Form Builder - Generate DocType Error")
        frappe.throw(_("Failed to generate DocType: {0}").format(str(e)))


@frappe.whitelist(allow_guest=True)
def approve_artifact(artifact_id=None, doc=None):
    """
    Approve and publish an AI-generated artifact.
    
    Args:
        artifact_id (str): The artifact ID to approve
        doc (str): JSON string of the document (fallback for incorrect API calls)
    
    Returns:
        dict: Approval confirmation
    """
    try:
        # Handle case where doc is passed instead of artifact_id
        if doc and not artifact_id:
            doc_dict = json.loads(doc)
            artifact_id = doc_dict.get('name')
        
        if not artifact_id:
            frappe.throw(_("Missing artifact_id"))
        
        # Check permissions
        if not frappe.has_permission("AI Generated Artifact", "write"):
            frappe.throw(_("Insufficient permissions to approve artifacts"), frappe.PermissionError)
        
        artifact = frappe.get_doc("AI Generated Artifact", artifact_id)
        
        if artifact.status == "approved":
            frappe.throw(_("Artifact is already approved"))
        
        spec = json.loads(artifact.content)
        
        # Create the DocType
        created_doctype = create_doctype_from_spec(spec, artifact_id)
        
        # Automatically create Web Form for public access
        try:
            web_form_route = create_web_form_for_approved_artifact(created_doctype.name, spec, artifact_id)
        except Exception as web_form_error:
            frappe.log_error(frappe.get_traceback(), "AI Form Builder - Web Form Creation Error")
            # Continue with approval even if Web Form creation fails
        
        # Update artifact status
        artifact.status = "approved"
        artifact.frappe_doctype = created_doctype.name
        artifact.approved_by = frappe.session.user
        artifact.save()
        frappe.db.commit()
        
        # Log audit trail
        doctype_name = spec.get("doctype_name") or spec.get("name")
        log_audit_action("approved", artifact_id, doctype_name)
        
        # Return success message with Web Form info if created
        response = {
            "message": _("Artifact approved and DocType created successfully"),
            "doctype_name": created_doctype.name
        }
        
        if 'web_form_route' in locals():
            response["web_form_url"] = f"/{web_form_route}"
            response["message"] += _(" Web Form created for public access.")
        
        return response
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "AI Form Builder - Approve Artifact Error")
        frappe.throw(_("Failed to approve artifact: {0}").format(str(e)))


@frappe.whitelist(allow_guest=True)
def reject_artifact(artifact_id=None, reason=None, doc=None):
    """
    Reject an AI-generated artifact.
    
    Args:
        artifact_id (str): The artifact ID to reject
        reason (str, optional): Reason for rejection
        doc (str): JSON string of the document (fallback for incorrect API calls)
    
    Returns:
        dict: Rejection confirmation
    """
    try:
        # Handle case where doc is passed instead of artifact_id
        if doc and not artifact_id:
            doc_dict = json.loads(doc)
            artifact_id = doc_dict.get('name')
        
        if not artifact_id:
            frappe.throw(_("Missing artifact_id"))
        
        # Check permissions
        if not frappe.has_permission("AI Generated Artifact", "write"):
            frappe.throw(_("Insufficient permissions to reject artifacts"), frappe.PermissionError)
        
        artifact = frappe.get_doc("AI Generated Artifact", artifact_id)
        artifact.status = "rejected"
        artifact.rejection_reason = reason
        artifact.save()
        frappe.db.commit()
        
        # Log audit trail
        log_audit_action("rejected", artifact_id, artifact.artifact_name, reason)
        
        return {
            "message": _("Artifact rejected"),
            "artifact_id": artifact_id
        }
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "AI Form Builder - Reject Artifact Error")
        frappe.throw(_("Failed to reject artifact: {0}").format(str(e)))


def create_doctype_from_spec(spec, artifact_id):
    """
    Create a Frappe DocType from specification.
    
    Args:
        spec (dict): DocType specification
        artifact_id (str): Reference to AI Generated Artifact
    
    Returns:
        Document: Created DocType document
    """
    try:
        # Build DocType dictionary
        doctype_name = spec.get("doctype_name") or spec.get("name")
        
        # Check if DocType already exists and make name unique
        if frappe.db.exists("DocType", doctype_name):
            # Append timestamp or counter to make it unique
            base_name = doctype_name
            counter = 1
            while frappe.db.exists("DocType", doctype_name):
                doctype_name = f"{base_name} {counter}"
                counter += 1
            frappe.msgprint(f"A DocType named '{base_name}' already exists. Creating as '{doctype_name}' instead.", indicator="orange", alert=True)
        
        # Handle naming rules
        naming_rule = spec.get("naming_rule", "Autoincrement")
        autoname = ""
        
        # If naming_rule looks like a format string, use it as autoname
        if naming_rule and naming_rule.startswith("format:"):
            autoname = naming_rule.replace("format:", "")
            naming_rule = "By \"Naming Series\" field"
        elif naming_rule == "Autoincrement":
            naming_rule = "Autoincrement"
        else:
            naming_rule = "Autoincrement"  # fallback
        
        # Fix autoname format for Frappe naming series (replace {#####} with .#####)
        if autoname and "{#####}" in autoname:
            autoname = autoname.replace("{#####}", ".#####")
        
        # Determine module and web settings based on accessibility preference
        is_web_accessible = spec.get("is_web_accessible", True)
        
        # Get module from spec, or use default based on web accessibility
        module = spec.get("module") or ("Website" if is_web_accessible else "Custom")
        
        if is_web_accessible:
            has_web_view = 1
            allow_guest_view = 1
            allow_guest_write = 1
            
            # Generate unique route for DocType
            base_route = doctype_name.lower().replace(" ", "-")
            route = base_route
            counter = 1
            # Check if route is already used by another DocType
            while frappe.db.exists("DocType", {"route": route, "name": ["!=", doctype_name]}):
                route = f"{base_route}-{counter}"
                counter += 1
            
            add_route_field = True
        else:
            has_web_view = 0
            allow_guest_view = 0
            allow_guest_write = 0
            route = None
            add_route_field = False
        
        doctype_dict = {
            "doctype": "DocType",
            "name": doctype_name,
            "module": module,
            "custom": 1,
            "fields": [],
            "permissions": [],
            "naming_rule": naming_rule,
            "autoname": autoname,
            "is_submittable": spec.get("is_submittable", 0),
            "track_changes": 1,
            "has_web_view": has_web_view,
            "allow_guest_to_view": allow_guest_view,
            "allow_guest_to_write": allow_guest_write,
            "route": route,
            "description": spec.get("description", f"Generated by AI Form Builder (Artifact: {artifact_id})")
        }
        
        # Fieldtype mapping: Convert AI-suggested types to valid Frappe types
        fieldtype_mapping = {
            "Email": "Data",  # Email is not a valid Frappe fieldtype, use Data instead
            "Text Area": "Small Text",
            "Textarea": "Small Text",
        }
        
        # Add fields
        for idx, field_spec in enumerate(spec.get("fields", [])):
            original_fieldtype = field_spec.get("fieldtype")
            # Map fieldtype if needed
            mapped_fieldtype = fieldtype_mapping.get(original_fieldtype, original_fieldtype)
            
            field = {
                "fieldname": field_spec.get("fieldname"),
                "label": field_spec.get("label"),
                "fieldtype": mapped_fieldtype,
                "mandatory": field_spec.get("mandatory", 0),
                "in_list_view": field_spec.get("in_list_view", 0),
                "in_standard_filter": field_spec.get("in_standard_filter", 0),
                "options": field_spec.get("options"),
                "default": field_spec.get("default"),
                "description": field_spec.get("description"),
                "idx": idx + 1
            }
            doctype_dict["fields"].append(field)
        
        # Add route field for web views (required for has_web_view=1)
        if add_route_field:
            doctype_dict["fields"].append({
                "fieldname": "route",
                "label": "Route",
                "fieldtype": "Data",
                "hidden": 1,
                "read_only": 1,
                "idx": len(doctype_dict["fields"]) + 1
            })
        
        # Add default permissions if none specified
        # Note: Not setting permissions here to avoid administrator-only restrictions
        # Permissions will be configured by administrators after DocType creation
        # The DocType will be created with basic access that can be modified later
        
        # Create the DocType
        doctype_doc = frappe.get_doc(doctype_dict)
        doctype_doc.insert(ignore_permissions=True)
        frappe.db.commit()
        
        return doctype_doc
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "AI Form Builder - Create DocType Error")
        raise e


def log_audit_action(action, artifact_id, artifact_name, reason=None):
    """Log an action in the audit trail."""
    try:
        audit_log = frappe.get_doc({
            "doctype": "AI Audit Log",
            "action": action,
            "artifact_id": artifact_id,
            "artifact_name": artifact_name,
            "actor": frappe.session.user,
            "reason": reason
        })
        audit_log.insert()
        frappe.db.commit()
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "AI Form Builder - Audit Log Error")


@frappe.whitelist()
def get_approved_artifacts():
    """Get list of approved artifacts"""
    artifacts = frappe.get_all("AI Generated Artifact", 
        filters={"status": "approved"},
        fields=["name", "artifact_name", "frappe_doctype", "status"]
    )
    return artifacts


@frappe.whitelist()
def check_doctype_config(doctype_name="Employee Onboarding"):
    """Check DocType configuration"""
    try:
        doctype = frappe.get_doc("DocType", doctype_name)
        return {
            "name": doctype.name,
            "has_web_view": getattr(doctype, 'has_web_view', None),
            "allow_guest_to_view": getattr(doctype, 'allow_guest_to_view', None),
            "route": getattr(doctype, 'route', None),
            "module": getattr(doctype, 'module', None),
            "is_submittable": getattr(doctype, 'is_submittable', None),
            "custom": getattr(doctype, 'custom', None)
        }
    except Exception as e:
        return {"error": str(e)}


@frappe.whitelist()
def check_web_form(doctype_name="Employee Onboarding"):
    """Check if Web Form exists for DocType"""
    web_form = frappe.db.exists("Web Form", {"doc_type": doctype_name})
    if web_form:
        return {"exists": True, "name": web_form}
    else:
        return {"exists": False, "message": f"No Web Form found for {doctype_name}"}


@frappe.whitelist()
def create_web_form_for_approved_artifact(doctype_name, spec, artifact_id):
    """
    Create a Web Form for an approved artifact with automatic setup.
    
    Args:
        doctype_name (str): Name of the created DocType
        spec (dict): The DocType specification
        artifact_id (str): The artifact ID
    
    Returns:
        str: The Web Form route
    """
    try:
        # Check if Web Form already exists
        if frappe.db.exists("Web Form", {"doc_type": doctype_name}):
            web_form = frappe.get_doc("Web Form", {"doc_type": doctype_name})
            return web_form.route
        
        # Generate a unique route based on doctype name
        base_route = doctype_name.lower().replace(' ', '-').replace('_', '-')
        route = base_route
        counter = 1
        
        # Ensure route is unique
        while frappe.db.exists("Web Form", {"route": route}):
            route = f"{base_route}-{counter}"
            counter += 1
        
        # Create Web Form
        web_form = frappe.get_doc({
            "doctype": "Web Form",
            "title": doctype_name,
            "doc_type": doctype_name,
            "module": "Website",
            "route": route,
            "is_standard": 0,
            "login_required": 0,
            "allow_multiple": 1,
            "show_sidebar": 0,
            "published": 1,  # Auto-publish
            "web_form_fields": []
        })
        
        # Get DocType to add fields
        doctype = frappe.get_doc("DocType", doctype_name)
        
        # Add fields to Web Form (exclude system fields)
        for field in doctype.fields:
            if field.fieldtype not in ['Column Break', 'Section Break', 'Tab Break'] and not field.hidden:
                web_form.append("web_form_fields", {
                    "fieldname": field.fieldname,
                    "label": field.label,
                    "fieldtype": field.fieldtype,
                    "reqd": field.reqd,
                    "options": field.options,
                    "description": field.description,
                    "idx": field.idx
                })
        
        web_form.insert(ignore_permissions=True)
        frappe.db.commit()
        
        # Create Public Forms record for listing
        public_form = frappe.get_doc({
            "doctype": "Public Forms",
            "title": doctype_name,
            "web_form": web_form.name,
            "route": route,
            "visit_link": f"/{route}"
        })
        public_form.insert(ignore_permissions=True)
        frappe.db.commit()
        
        # Set up DocType for Web Form compatibility
        # Remove route conflict and disable web view
        doctype.route = None
        doctype.has_web_view = 0
        doctype.allow_guest_to_view = 0
        doctype.save()
        
        # Add guest permissions
        doctype.append("permissions", {
            "role": "Guest",
            "read": 1,
            "write": 1,
            "create": 1,
            "submit": 0,
            "cancel": 0,
            "amend": 0
        })
        doctype.save()
        frappe.db.commit()
        
        return route
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "AI Form Builder - Auto Web Form Creation Error")
        raise e
    """Check Web Form configuration details"""
    try:
        web_form = frappe.get_doc("Web Form", web_form_name)
        return {
            "name": web_form.name,
            "title": web_form.title,
            "doc_type": web_form.doc_type,
            "route": web_form.route,
            "is_standard": web_form.is_standard,
            "login_required": web_form.login_required,
            "allow_multiple": web_form.allow_multiple,
            "published": web_form.published if hasattr(web_form, 'published') else None,
            "disabled": web_form.disabled if hasattr(web_form, 'disabled') else None,
            "field_count": len(web_form.web_form_fields) if hasattr(web_form, 'web_form_fields') else 0
        }
    except Exception as e:
        return {"error": str(e)}


@frappe.whitelist()
def publish_web_form(web_form_name="employee-onboarding"):
    """Publish the Web Form"""
    try:
        web_form = frappe.get_doc("Web Form", web_form_name)
        web_form.published = 1
        web_form.save()
        frappe.db.commit()
        return {"message": f"Web Form {web_form_name} published successfully"}
    except Exception as e:
        return {"error": str(e)}


@frappe.whitelist(allow_guest=True)
def fix_route_conflict(doctype_name="Employee Onboarding"):
    """Fix route conflict by removing DocType route when Web Form exists"""
    try:
        # Remove route from DocType to avoid conflict with Web Form
        doctype = frappe.get_doc("DocType", doctype_name)
        doctype.route = None
        doctype.save()
        frappe.db.commit()
        
        return {"message": f"Removed route from DocType {doctype_name} to allow Web Form to take precedence"}
    except Exception as e:
        return {"error": str(e)}


@frappe.whitelist()
def disable_doctype_web_view(doctype_name="Employee Onboarding"):
    """Disable web view on DocType to prevent conflicts with Web Form"""
    try:
        doctype = frappe.get_doc("DocType", doctype_name)
        doctype.has_web_view = 0
        doctype.allow_guest_to_view = 0
        doctype.save()
        frappe.db.commit()
        
        return {"message": f"Disabled web view on DocType {doctype_name}"}
    except Exception as e:
        return {"error": str(e)}


@frappe.whitelist()
def add_guest_permissions(doctype_name="Employee Onboarding"):
    """Add guest permissions to allow public access to the DocType"""
    try:
        doctype = frappe.get_doc("DocType", doctype_name)
        
        # Add guest permissions for web access
        doctype.append("permissions", {
            "role": "Guest",
            "read": 1,
            "write": 1,
            "create": 1,
            "submit": 0,
            "cancel": 0,
            "amend": 0
        })
        
        doctype.save()
        frappe.db.commit()
        
        return {"message": f"Added guest permissions to DocType {doctype_name}"}
    except Exception as e:
        return {"error": str(e)}


@frappe.whitelist()
def change_web_form_route(new_route="employee-onboarding-form"):
    """Change the Web Form route to avoid conflicts"""
    try:
        web_form = frappe.get_doc("Web Form", "employee-onboarding")
        web_form.route = new_route
        web_form.save()
        frappe.db.commit()
        
        return {"message": f"Changed Web Form route to {new_route}"}
    except Exception as e:
        return {"error": str(e)}


@frappe.whitelist()
def create_web_form(doctype_name="Employee Onboarding"):
    """Create a Web Form for the DocType"""
    try:
        # Check if Web Form already exists
        if frappe.db.exists("Web Form", {"doc_type": doctype_name}):
            return {"message": f"Web Form already exists for {doctype_name}"}
        
        # Get DocType fields
        doctype = frappe.get_doc("DocType", doctype_name)
        
        # Create Web Form
        web_form = frappe.get_doc({
            "doctype": "Web Form",
            "title": doctype_name,
            "doc_type": doctype_name,
            "module": getattr(doctype, 'module', 'Custom'),
            "route": getattr(doctype, 'route', doctype_name.lower().replace(' ', '-')),
            "is_standard": 0,
            "login_required": 0,
            "allow_multiple": 1,
            "show_sidebar": 0,
            "web_form_fields": []
        })
        
        # Add fields to Web Form (exclude system fields)
        for field in doctype.fields:
            if field.fieldtype not in ['Column Break', 'Section Break', 'Tab Break'] and not field.hidden:
                web_form.append("web_form_fields", {
                    "fieldname": field.fieldname,
                    "label": field.label,
                    "fieldtype": field.fieldtype,
                    "reqd": field.reqd,
                    "options": field.options,
                    "description": field.description,
                    "idx": field.idx
                })
        
        web_form.insert(ignore_permissions=True)
        frappe.db.commit()
        
        return {
            "message": f"Web Form created for {doctype_name}",
            "route": web_form.route
        }
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "AI Form Builder - Create Web Form Error")
        return {"error": str(e)}
