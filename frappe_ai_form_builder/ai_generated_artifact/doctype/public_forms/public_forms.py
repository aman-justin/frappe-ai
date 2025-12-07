# -*- coding: utf-8 -*-
# Copyright (c) 2024, Frappe AI Form Builder and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class PublicForms(Document):
	def before_save(self):
		"""Calculate submission count and set view submissions link"""
		if self.web_form:
			# Get the Web Form document to find the DocType
			web_form_doc = frappe.get_doc("Web Form", self.web_form)
			if web_form_doc.doc_type:
				doctype_name = web_form_doc.doc_type
				
				# Count submissions
				try:
					submission_count = frappe.db.count(doctype_name)
					self.submission_count = submission_count
				except:
					self.submission_count = 0
				
				# Set view submissions link (for admin access)
				doctype_slug = doctype_name.lower().replace(' ', '-').replace('_', '-')
				view_url = f"/app/{doctype_slug}"
				self.view_submissions = f'<a href="{view_url}" target="_blank" class="btn btn-sm btn-primary">View {submission_count} Submissions</a>'