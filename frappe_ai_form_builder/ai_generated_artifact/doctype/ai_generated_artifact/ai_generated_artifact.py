# AI Generated Artifact DocType controller

import frappe
from frappe.model.document import Document

class AIGeneratedArtifact(Document):
	def validate(self):
		# Set created_by if not set
		if not self.created_by:
			self.created_by = frappe.session.user

	def before_save(self):
		# Prevent direct status changes to approved/rejected by non-admins
		if self.has_value_changed("status"):
			if self.status in ["approved", "rejected"] and not frappe.has_permission("AI Generated Artifact", "write", user=frappe.session.user):
				frappe.throw(_("Only System Managers can approve or reject artifacts"))

	def on_update(self):
		# Log status changes
		if self.has_value_changed("status"):
			frappe.get_doc({
				"doctype": "AI Audit Log",
				"action": self.status,
				"artifact_id": self.name,
				"artifact_name": self.artifact_name,
				"actor": frappe.session.user
			}).insert(ignore_permissions=True)

