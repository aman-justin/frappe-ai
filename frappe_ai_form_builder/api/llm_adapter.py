"""LLM Adapter for AI Form Builder - Integrates with OpenAI/Anthropic"""

import frappe
from frappe import _
import json
import os


def get_llm_response(conversation_history, user_message):
    """
    Get response from LLM provider (OpenAI, Anthropic, or Gemini).
    
    Args:
        conversation_history (list): Previous conversation messages
        user_message (str): Latest user message
    
    Returns:
        dict: LLM response with message, draft_spec, suggestions
    """
    provider = frappe.db.get_single_value("AI Config", "llm_provider") or "gemini"
    
    if provider == "openai":
        return get_openai_response(conversation_history, user_message)
    elif provider == "anthropic":
        return get_anthropic_response(conversation_history, user_message)
    elif provider == "gemini":
        return get_gemini_response(conversation_history, user_message)
    else:
        frappe.throw(_("Unsupported LLM provider: {0}").format(provider))


def get_openai_response(conversation_history, user_message):
    """Get response from OpenAI GPT-4."""
    try:
        import openai
        
        # Get API key from AI Config
        api_key = get_api_key("openai")
        
        client = openai.OpenAI(api_key=api_key)
        
        # Build messages for OpenAI
        messages = [
            {"role": "system", "content": get_system_prompt()}
        ]
        
        # Add conversation history
        for msg in conversation_history:
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        # Add current user message
        messages.append({"role": "user", "content": user_message})
        
        # Get selected model from AI Config
        model_name = frappe.db.get_single_value("AI Config", "openai_model") or "gpt-4"
        
        # Call OpenAI API
        response = client.chat.completions.create(
            model=model_name,
            messages=messages,
            temperature=0.7,
            max_tokens=2000
        )
        
        assistant_message = response.choices[0].message.content
        
        # Parse response for structured data
        parsed_response = parse_llm_response(assistant_message)
        
        return parsed_response
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "AI Form Builder - OpenAI Error")
        frappe.throw(_("Failed to get OpenAI response: {0}").format(str(e)))


def get_anthropic_response(conversation_history, user_message):
    """Get response from Anthropic Claude."""
    try:
        import anthropic
        
        # Get API key from AI Config
        api_key = get_api_key("anthropic")
        
        client = anthropic.Anthropic(api_key=api_key)
        
        # Build messages for Claude
        messages = []
        
        # Add conversation history
        for msg in conversation_history:
            if msg["role"] != "system":
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
        
        # Add current user message
        messages.append({"role": "user", "content": user_message})
        
        # Get selected model from AI Config
        model_name = frappe.db.get_single_value("AI Config", "anthropic_model") or "claude-3-sonnet-20240229"
        
        # Call Anthropic API
        response = client.messages.create(
            model=model_name,
            max_tokens=2000,
            system=get_system_prompt(),
            messages=messages
        )
        
        assistant_message = response.content[0].text
        
        # Parse response for structured data
        parsed_response = parse_llm_response(assistant_message)
        
        return parsed_response
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "AI Form Builder - Anthropic Error")
        frappe.throw(_("Failed to get Anthropic response: {0}").format(str(e)))


def get_gemini_response(conversation_history, user_message):
    """Get response from Google Gemini."""
    try:
        import google.generativeai as genai
        
        # Get API key from AI Config
        api_key = get_api_key("gemini")
        
        genai.configure(api_key=api_key)
        
        # Get selected model from AI Config (force fresh read from DB, not cache)
        frappe.cache().hdel("singles", "AI Config")
        model_name = frappe.db.get_single_value("AI Config", "gemini_model", cache=False) or "gemini-2.5-flash"
        
        # Log which model is being used
        frappe.logger().info(f"Using Gemini model: {model_name}")
        
        # Initialize the model
        model = genai.GenerativeModel(model_name)
        
        # Build conversation for Gemini
        chat_history = []
        
        # Add conversation history
        for msg in conversation_history:
            if msg["role"] == "user":
                chat_history.append({"role": "user", "parts": [msg["content"]]})
            elif msg["role"] == "assistant":
                chat_history.append({"role": "model", "parts": [msg["content"]]})
        
        # Start chat with history
        chat = model.start_chat(history=chat_history)
        
        # Send message with system prompt included in first message if it's the first interaction
        if not conversation_history:
            full_message = f"{get_system_prompt()}\n\n{user_message}"
        else:
            full_message = user_message
        
        # Get response
        response = chat.send_message(full_message)
        assistant_message = response.text
        
        # Check if AI is writing tutorials instead of JSON
        tutorial_indicators = [
            "## ",  # Markdown headers
            "### ",
            "**Steps",
            "**Part ",
            "follow these steps",
            "go to awesome bar",
            "click **\"new\"**",
            "fill in the details:",
            "client script",
            "web form for",
            len(assistant_message) > 3000  # Way too long
        ]
        
        if any(indicator in assistant_message.lower() if isinstance(indicator, str) else indicator for indicator in tutorial_indicators):
            # AI is being stupid and writing a tutorial. Force a simple response.
            frappe.logger().warning(f"AI wrote tutorial ({len(assistant_message)} chars). Regenerating with stricter prompt.")
            
            retry_message = f"{get_system_prompt()}\n\nSTOP WRITING TUTORIALS! Just output ONE JSON spec in this EXACT format:\n\n```json\n{{\n  \"doctype_name\": \"Form Name\",\n  \"fields\": [...]\n}}\n```\n\nUser request: {user_message}"
            
            response = chat.send_message(retry_message)
            assistant_message = response.text
        
        # Parse response for structured data
        parsed_response = parse_llm_response(assistant_message)
        
        return parsed_response
        
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "AI Form Builder - Gemini Error")
        frappe.throw(_("Failed to get Gemini response: {0}").format(str(e)))


def get_api_key(provider):
    """
    Get API key for the specified provider from AI Config.
    
    Args:
        provider (str): The LLM provider ('gemini', 'openai', 'anthropic')
    
    Returns:
        str: The API key
    """
    field_name = f"{provider}_api_key"
    api_key = frappe.db.get_single_value("AI Config", field_name)
    if not api_key or not api_key.strip():
        frappe.throw(_("{0} API key not configured. Please set it in AI Config.").format(provider.title()))
    return api_key.strip()


def get_system_prompt():
    """
    Get system prompt from AI Config or use default.
    """
    default_prompt = """You are an expert AI assistant helping users create forms (DocTypes) in Frappe Framework.

YOUR CONVERSATION STRATEGY:
1. **First Messages**: Ask clarifying questions to understand their needs
   - What is the form for?
   - What fields do they need?
   - Which fields should be mandatory?
   - What field types (text, email, rating, date, etc.)?
   - Any validation rules or special requirements?

2. **Confirm Before Generating**: Once you understand their needs, summarize what you'll create and ask for confirmation

3. **Generate Only When Ready**: ONLY after the user confirms or provides complete details, include the JSON spec

CRITICAL RULES:
- You are building FRAPPE DOCTYPES, not HTML forms or generic templates
- NEVER write HTML, CSS, or web form code
- ONLY output conversational text + JSON specification
- The JSON will be used to create a Frappe DocType automatically
- Do NOT include JSON in your first few responses - only when ready to generate

Your role:
1. Have a natural conversation to understand what form the user needs
2. Ask about fields, field types, mandatory requirements, validations
3. Summarize and confirm before generating
4. Generate ONLY a Frappe DocType JSON specification (not HTML/templates)

Frappe DocType Field Types:
- Data: Short text (max 140 chars)
- Email: Email address with validation
- Small Text: Multi-line text area
- Text: Long text field
- Rating: Star rating (set options to max stars, e.g., "5" for 5 stars)
- Select: Dropdown with predefined options
- Link: Reference to another DocType
- Date: Date picker
- Datetime: Date and time picker
- Check: Boolean checkbox
- Int: Integer number
- Float: Decimal number
- Currency: Money amount
- Attach: File attachment
- Section Break: Visual separator
- Column Break: Column separator

JSON Format (ALWAYS include this):
```json
{
  "doctype_name": "Form Name",
  "module": "Website",
  "is_single": false,
  "is_submittable": false,
  "autoname": "autoincrement",
  "title_field": "primary_field_name",
  "is_web_accessible": true,
  "fields": [
    {
      "fieldname": "field_name",
      "label": "Field Label",
      "fieldtype": "Data",
      "mandatory": true,
      "description": "Help text"
    }
  ]
}
```

Important Rules:
- Use lowercase fieldnames with underscores (e.g., customer_name)
- Set mandatory: true for required fields
- For Rating fields, set options to the number of stars (e.g., "5")
- For Section Break, use fieldtype: "Section Break"
- Set is_web_accessible: true for public forms
- Be conversational and ask questions to clarify requirements
- ONLY include JSON when you have all information and are ready to generate

Example Conversation Flow:

User: "I need a customer feedback form"
You: "Great! I can help you create a customer feedback form. Let me understand your requirements:
- What information do you want to collect from customers? (name, email, etc.)
- Do you want rating scales? If yes, for what aspects and how many stars?
- Which fields should be mandatory?
- Any specific validations needed?"

User: "I need name, email (both mandatory), and 5-star ratings for overall experience, product quality, and support"
You: "Perfect! Let me confirm:
- Customer Name (mandatory)
- Customer Email (mandatory)  
- Overall Experience (5-star rating)
- Product Quality (5-star rating)
- Support (5-star rating)

Should I also add a comments/feedback text field? And should this be accessible to the public?"

User: "Yes, add a comments field and make it public"
You: "Perfect! I'll create your customer feedback form as a Frappe DocType. Here's the specification:

```json
{
  "doctype_name": "Customer Feedback",
  "module": "Website",
  "is_web_accessible": true,
  "autoname": "autoincrement",
  "title_field": "customer_name",
  "fields": [
    {
      "fieldname": "customer_name",
      "label": "Customer Name",
      "fieldtype": "Data",
      "mandatory": true
    },
    {
      "fieldname": "customer_email",
      "label": "Customer Email",
      "fieldtype": "Email",
      "mandatory": true
    },
    {
      "fieldname": "overall_experience",
      "label": "Overall Experience",
      "fieldtype": "Rating",
      "options": "5"
    },
    {
      "fieldname": "comments",
      "label": "Comments",
      "fieldtype": "Small Text"
    }
  ]
}
```

Click the 'Create Form' button to generate this DocType in Frappe!"

REMEMBER: Never write HTML templates or code. Always output Frappe DocType JSON specifications only.
"""
    
    try:
        system_prompt = frappe.db.get_single_value("AI Config", "system_prompt")
        # If custom prompt exists, use it; otherwise use default
        return system_prompt if system_prompt else default_prompt
    except Exception:
        # Fallback to default prompt if AI Config is not available
        return default_prompt
        return system_prompt or """You are an expert AI assistant helping users create forms (DocTypes) in Frappe Framework.

Your role:
1. Ask clarifying questions to understand what form the user needs
2. Gather information about fields, field types, validations, and relationships
3. Once you have ALL the information needed to generate the form, ask about web accessibility
4. Generate a valid Frappe DocType JSON specification
5. Explain your suggestions in simple terms

Frappe DocType Field Types:
- Data: Short text (max 140 chars)
- Text: Long text
- Select: Dropdown with predefined options
- Link: Reference to another DocType
- Date: Date picker
- Datetime: Date and time picker
- Check: Boolean checkbox
- Int: Integer number
- Float: Decimal number
- Currency: Money amount
- Attach: File upload
- Table: Child table (requires child DocType)

Field Naming Rules:
- Use lowercase with underscores (snake_case)
- No spaces or special characters
- Max 140 characters
- NEVER use 'name' as a fieldname (it's reserved for the record ID)
- Cannot use reserved names: owner, creation, modified, modified_by, docstatus

Web Accessibility Question:
ONLY ask about web accessibility AFTER you have gathered ALL the information needed to generate the form (all fields, types, validations, etc.). Ask: "Should this form be accessible on the web for public submissions, or is it for internal/admin use only?"
If the user doesn't specify, assume public access (is_web_accessible: true).

When you have enough information, generate a JSON specification like this:
```json
{
  "doctype_name": "Employee Onboarding",
  "module": "HR",
  "is_web_accessible": false,
  "fields": [
    {
      "fieldname": "employee_name",
      "label": "Employee Name",
      "fieldtype": "Data",
      "mandatory": 1,
      "in_list_view": 1
    },
    {
      "fieldname": "start_date",
      "label": "Start Date",
      "fieldtype": "Date",
      "mandatory": 1
    }
  ],
  "naming_rule": "autoincrement",
  "is_submittable": 0
}
```

Important:
- Always ask clarifying questions before generating
- Gather ALL form requirements first (fields, types, validations, etc.)
- ONLY after you have complete form specifications, ask about web accessibility
- Validate field names follow naming rules
- For Link fields, ask which DocType to link to
- For Select fields, ask for the list of options
- Be conversational and helpful
- If unsure, ask rather than assume
- Set "is_web_accessible": true for public forms, false for internal forms (default is true for public access)

When ready to generate, include the JSON spec in your response wrapped in ```json markers."""


def parse_llm_response(response_text):
    """
    Parse LLM response to extract structured data.
    
    Args:
        response_text (str): Raw LLM response
    
    Returns:
        dict: Parsed response with message, draft_spec, suggestions
    """
    result = {
        "message": response_text,
        "draft_spec": None,
        "suggestions": [],
        "ready_to_generate": False
    }
    
    # Try to extract JSON spec from response
    if "```json" in response_text:
        try:
            # Extract JSON between ```json and ```
            start = response_text.find("```json") + 7
            end = response_text.find("```", start)
            json_str = response_text[start:end].strip()
            
            draft_spec = json.loads(json_str)
            
            # Check if this is a full DocType export (has 'doctype': 'DocType') or our simple format
            if draft_spec.get("doctype") == "DocType":
                # This is a full Frappe DocType export - extract the relevant parts
                simplified_spec = {
                    "doctype_name": draft_spec.get("name"),
                    "module": draft_spec.get("module", "Custom"),
                    "is_single": draft_spec.get("issingle", 0) == 1,
                    "is_submittable": draft_spec.get("is_submittable", 0) == 1,
                    "autoname": draft_spec.get("autoname", "autoincrement"),
                    "title_field": draft_spec.get("title_field"),
                    "is_web_accessible": draft_spec.get("is_web_accessible", 1) == 1,
                    "allow_guest_to_save": draft_spec.get("allow_guests", 0) == 1,
                    "fields": []
                }
                
                # Convert full field format to simplified format
                for field in draft_spec.get("fields", []):
                    simplified_field = {
                        "fieldname": field.get("fieldname"),
                        "label": field.get("label"),
                        "fieldtype": field.get("fieldtype"),
                        "mandatory": field.get("reqd", 0) == 1,
                        "options": field.get("options", ""),
                        "description": field.get("description", ""),
                        "default": field.get("default", ""),
                        "depends_on": field.get("depends_on", "")
                    }
                    # Remove empty values
                    simplified_field = {k: v for k, v in simplified_field.items() if v or k in ["fieldname", "label", "fieldtype", "mandatory"]}
                    simplified_spec["fields"].append(simplified_field)
                
                draft_spec = simplified_spec
            
            result["draft_spec"] = draft_spec
            result["ready_to_generate"] = True
            
            # Validate the spec
            validation_errors = validate_doctype_spec(draft_spec)
            if validation_errors:
                result["message"] += f"\n\n⚠️ Validation issues found:\n" + "\n".join(validation_errors)
                result["ready_to_generate"] = False
                
        except json.JSONDecodeError as e:
            frappe.log_error(f"Failed to parse JSON from LLM response: {str(e)}", "AI Form Builder - JSON Parse Error")
    
    # Check for conversational ready signals
    ready_signals = [
        "click the \"create form\" button",
        "click the create form button", 
        "ready to generate",
        "form specification has been generated",
        "you can now create the form"
    ]
    
    if any(signal in response_text.lower() for signal in ready_signals):
        result["ready_to_generate"] = True
    
    return result


def validate_doctype_spec(spec):
    """
    Validate DocType specification against Frappe schema rules.
    
    Args:
        spec (dict): DocType specification
    
    Returns:
        list: List of validation error messages (empty if valid)
    """
    errors = []
    
    # Check required fields
    doctype_name = spec.get("doctype_name") or spec.get("name")
    if not doctype_name:
        errors.append("DocType name is required")
    
    if not spec.get("fields") or not isinstance(spec["fields"], list):
        errors.append("Fields array is required")
    
    # Validate field names
    # reserved_names = ["name", "owner", "creation", "modified", "modified_by", "docstatus"]  # Skip for MVP
    reserved_names = ["owner", "creation", "modified", "modified_by", "docstatus"]  # Allow 'name' for custom fields
    allowed_fieldtypes = [
        "Data", "Text", "Long Text", "Small Text", "Text Area", "Select", "Link", "Date", "Datetime", "Time",
        "Check", "Int", "Float", "Currency", "Attach", "Attach Image", "Table",
        "Section Break", "Column Break", "HTML", "Button", "Code", "Text Editor",
        "Markdown Editor", "HTML Editor", "Read Only", "Password",
        "Phone", "Email", "Autocomplete", "Barcode", "Color", "Duration", "Rating",
        "Geolocation", "Dynamic Link", "Table MultiSelect", "Signature", "Icon"
    ]
    
    # Field types that don't require fieldname
    non_fieldname_types = ["Section Break", "Column Break", "HTML", "Button"]
    
    for field in spec.get("fields", []):
        fieldtype = field.get("fieldtype")
        fieldname = field.get("fieldname", "")
        
        # Check fieldtype is valid
        if fieldtype not in allowed_fieldtypes:
            errors.append(f"Field has invalid fieldtype: {fieldtype}")
            continue
        
        # Skip fieldname validation for Section Break, Column Break, etc.
        if fieldtype in non_fieldname_types:
            continue
        
        # Check fieldname format for regular fields
        if not fieldname:
            errors.append(f"Field with type '{fieldtype}' is missing fieldname")
            continue
            
        if fieldname in reserved_names:
            errors.append(f"Field '{fieldname}' uses a reserved name")
        
        if not fieldname.islower() or not fieldname.replace("_", "").isalnum():
            errors.append(f"Field '{fieldname}' must be lowercase with underscores only")
        
        if len(fieldname) > 140:
            errors.append(f"Field '{fieldname}' exceeds 140 character limit")
        
        # Check Link fields have options
        if fieldtype == "Link" and not field.get("options"):
            errors.append(f"Link field '{fieldname}' must specify options (target DocType)")
    
    return errors
