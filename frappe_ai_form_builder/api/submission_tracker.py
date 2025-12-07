# -*- coding: utf-8 -*-
# Copyright (c) 2024, Frappe AI Form Builder and contributors
# For license information, please see license.txt

import frappe
import json
from frappe.utils import get_datetime

def track_submission(doc, method):
	"""Track form submissions in the unified Form Submissions DocType"""

	# Only track if this was submitted via a web form
	if not hasattr(frappe.flags, 'in_web_form') or not frappe.flags.in_web_form:
		return

	# Check if this doctype has a web form
	web_form_exists = frappe.db.exists("Web Form", {"doc_type": doc.doctype})
	if not web_form_exists:
		return

	try:
		# Get the web form name
		web_form_name = frappe.db.get_value("Web Form", {"doc_type": doc.doctype}, "name")
		if not web_form_name:
			return

		# Prepare submission data
		submission_data = {}
		meta = frappe.get_meta(doc.doctype)

		# Get all field values
		for field in meta.fields:
			if field.fieldname and field.fieldname != 'name':
				value = doc.get(field.fieldname)
				if value is not None:
					submission_data[field.fieldname] = str(value)

		# Create Form Submissions record
		submission = frappe.get_doc({
			"doctype": "Form Submissions",
			"form_name": web_form_name,
			"form_type": doc.doctype,
			"submitted_by": frappe.session.user if frappe.session.user != "Guest" else "Anonymous",
			"submission_date": get_datetime(),
			"submission_data": json.dumps(submission_data, indent=2),
			"status": "New",
			"ip_address": getattr(frappe.local, 'request_ip', None),
			"user_agent": getattr(frappe.local, 'user_agent', None)
		})

		submission.insert(ignore_permissions=True)
		frappe.db.commit()

	except Exception as e:
		# Log error but don't break the submission
		frappe.log_error(f"Form submission tracking failed: {str(e)}", "Form Submission Tracker")