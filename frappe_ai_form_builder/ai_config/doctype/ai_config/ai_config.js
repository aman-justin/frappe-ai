// Copyright (c) 2025, Your Name and contributors
// For license information, please see license.txt

frappe.ui.form.on("AI Config", {
	refresh(frm) {
		// Show current model selection clearly
		if (frm.doc.llm_provider) {
			const model_field = frm.doc.llm_provider + '_model';
			const current_model = frm.doc[model_field];
			if (current_model) {
				frm.set_intro(`Current provider: <b>${frm.doc.llm_provider}</b>, Model: <b>${current_model}</b>`, 'blue');
			}
		}
	},
	
	after_save(frm) {
		// Show success message with current settings
		const model_field = frm.doc.llm_provider + '_model';
		const current_model = frm.doc[model_field];
		frappe.show_alert({
			message: `AI Config saved! Now using <b>${frm.doc.llm_provider}</b> with model <b>${current_model}</b>`,
			indicator: 'green'
		}, 10);
	},
	
	llm_provider(frm) {
		// Update intro when provider changes
		frm.trigger('refresh');
	}
});
