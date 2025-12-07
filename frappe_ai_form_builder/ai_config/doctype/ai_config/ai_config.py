# AI Config DocType controller

import frappe
from frappe.model.document import Document

class AIConfig(Document):
    def validate(self):
        """Validate AI Config settings"""
        # Ensure API key is set for selected provider
        if self.llm_provider == "gemini" and not self.gemini_api_key:
            frappe.throw("Please enter Gemini API Key")
        elif self.llm_provider == "openai" and not self.openai_api_key:
            frappe.throw("Please enter OpenAI API Key")
        elif self.llm_provider == "anthropic" and not self.anthropic_api_key:
            frappe.throw("Please enter Anthropic API Key")
    
    def on_update(self):
        """Clear cache after updating AI Config"""
        # Clear single value cache for all fields
        frappe.cache().hdel("singles", "AI Config")
        frappe.clear_cache(doctype="AI Config")
        
        # Log the change
        frappe.logger().info(f"AI Config updated - Provider: {self.llm_provider}, Model: {self.get(f'{self.llm_provider}_model')}")
