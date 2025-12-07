"""Frappe AI Form Builder Hooks"""

from . import __version__ as app_version

app_name = "frappe_ai_form_builder"
app_title = "Frappe AI Form Builder"
app_publisher = "Your Name"
app_description = "AI-powered form and template generator for Frappe"
app_email = "your.email@example.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
app_include_css = "/assets/frappe_ai_form_builder/css/frappe_ai_form_builder.css"
app_include_js = "/assets/frappe_ai_form_builder/js/frappe_ai_form_builder.js"

# include js, css files in header of web template
# web_include_css = "/assets/frappe_ai_form_builder/css/frappe_ai_form_builder.css"
# web_include_js = "/assets/frappe_ai_form_builder/js/frappe_ai_form_builder.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "frappe_ai_form_builder/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "frappe_ai_form_builder.utils.jinja_methods",
# 	"filters": "frappe_ai_form_builder.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "frappe_ai_form_builder.install.before_install"
# after_install = "frappe_ai_form_builder.install.after_install"

# Fixtures
# --------

fixtures = [
    {
        "doctype": "Workspace",
        "filters": [
            ["name", "in", ["AI Form Builder"]]
        ]
    },
    {
        "doctype": "Workspace Sidebar",
        "filters": [
            ["name", "in", ["AI Form Builder"]]
        ]
    }
]

# Uninstallation
# ------------

# before_uninstall = "frappe_ai_form_builder.uninstall.before_uninstall"
# after_uninstall = "frappe_ai_form_builder.uninstall.after_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "frappe_ai_form_builder.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

doc_events = {
	"*": {
		"after_insert": "frappe_ai_form_builder.api.submission_tracker.track_submission"
	}
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"frappe_ai_form_builder.tasks.all"
# 	],
# 	"daily": [
# 		"frappe_ai_form_builder.tasks.daily"
# 	],
# 	"hourly": [
# 		"frappe_ai_form_builder.tasks.hourly"
# 	],
# 	"weekly": [
# 		"frappe_ai_form_builder.tasks.weekly"
# 	],
# 	"monthly": [
# 		"frappe_ai_form_builder.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "frappe_ai_form_builder.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "frappe_ai_form_builder.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps

# Whitelisted Methods
# -------------------

whitelisted_methods = [
    "frappe_ai_form_builder.api.session.start_session",
    "frappe_ai_form_builder.api.session.send_message",
    "frappe_ai_form_builder.api.generator.generate_doctype",
    "frappe_ai_form_builder.api.generator.approve_artifact",
    "frappe_ai_form_builder.api.generator.reject_artifact"
]
# override_doctype_dashboards = {
# 	"Task": "frappe_ai_form_builder.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["frappe_ai_form_builder.utils.before_request"]
# after_request = ["frappe_ai_form_builder.utils.after_request"]

# Job Events
# ----------
# before_job = ["frappe_ai_form_builder.utils.before_job"]
# after_job = ["frappe_ai_form_builder.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"frappe_ai_form_builder.auth.validate"
# ]
