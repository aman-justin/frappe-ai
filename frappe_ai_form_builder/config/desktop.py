"""Desktop configuration for Frappe AI Form Builder"""

from frappe import _


def get_data():
    """Return desktop icons for AI Form Builder"""
    return [
        {
            "module_name": "AI Form Builder",
            "category": "Modules",
            "label": _("AI Form Builder"),
            "color": "#4C51BF",
            "icon": "octicon octicon-hubot",
            "type": "module",
            "description": "AI-powered form and template generator",
            "onboard": False,
        }
    ]
