// Copyright (c) 2025, Your Name and contributors
// For license information, please see license.txt

frappe.listview_settings["AI Generated Artifact"] = {
	add_fields: ["status", "artifact_type"],
	get_indicator: function(doc) {
		if (doc.status === "approved") {
			return [__("Approved"), "green", "status,=,approved"];
		} else if (doc.status === "rejected") {
			return [__("Rejected"), "red", "status,=,rejected"];
		} else {
			return [__("Draft"), "orange", "status,=,draft"];
		}
	},
	formatters: {
		status: function(value, field, doc) {
			if (value === "draft") {
				return '<span class="indicator-pill orange">Draft</span> <button class="btn btn-xs btn-success" onclick="approve_artifact(\'' + doc.name + '\')">Approve</button> <button class="btn btn-xs btn-danger" onclick="reject_artifact(\'' + doc.name + '\')">Reject</button>';
			} else if (value === "approved") {
				return '<span class="indicator-pill green">Approved</span>';
			} else if (value === "rejected") {
				return '<span class="indicator-pill red">Rejected</span>';
			}
			return value;
		}
	},
	get_actions: function() {
		if (frappe.user.has_role("System Manager")) {
			return [
				{
					label: __("Approve Selected"),
					action: function() {
						let selected = cur_list.get_checked_items();
						if (selected.length === 0) {
							frappe.msgprint(__("Please select artifacts to approve"));
							return;
						}
						
						let draft_items = selected.filter(item => item.status === 'draft');
						if (draft_items.length === 0) {
							frappe.msgprint(__("No draft artifacts selected"));
							return;
						}
						
						frappe.confirm(
							`Are you sure you want to approve ${draft_items.length} artifact(s)? This will create the DocTypes.`,
							function() {
								let success_count = 0;
								let error_count = 0;
								
								draft_items.forEach(item => {
									frappe.call({
										method: 'frappe_ai_form_builder.api.generator.approve_artifact',
										args: { artifact_id: item.name },
										callback: function(r) {
											if (r.message) {
												success_count++;
											} else {
												error_count++;
											}
											
											// Refresh when all calls are done
											if (success_count + error_count === draft_items.length) {
												if (success_count > 0) {
													frappe.msgprint(`Approved ${success_count} artifact(s) successfully!`);
												}
												if (error_count > 0) {
													frappe.msgprint(`Failed to approve ${error_count} artifact(s)`);
												}
												cur_list.refresh();
											}
										}
									});
								});
							}
						);
					}
				},
				{
					label: __("Reject Selected"),
					action: function() {
						let selected = cur_list.get_checked_items();
						if (selected.length === 0) {
							frappe.msgprint(__("Please select artifacts to reject"));
							return;
						}
						
						let draft_items = selected.filter(item => item.status === 'draft');
						if (draft_items.length === 0) {
							frappe.msgprint(__("No draft artifacts selected"));
							return;
						}
						
						let d = new frappe.ui.Dialog({
							title: __("Reject Artifacts"),
							fields: [
								{
									fieldname: 'reason',
									fieldtype: 'Text',
									label: __("Rejection Reason"),
									reqd: 1
								}
							],
							primary_action_label: __("Reject"),
							primary_action: function(values) {
								let success_count = 0;
								let error_count = 0;
								
								draft_items.forEach(item => {
									frappe.call({
										method: 'frappe_ai_form_builder.api.generator.reject_artifact',
										args: {
											artifact_id: item.name,
											reason: values.reason
										},
										callback: function(r) {
											if (r.message) {
												success_count++;
											} else {
												error_count++;
											}
											
											// Refresh when all calls are done
											if (success_count + error_count === draft_items.length) {
												if (success_count > 0) {
													frappe.msgprint(`Rejected ${success_count} artifact(s)`);
												}
												if (error_count > 0) {
													frappe.msgprint(`Failed to reject ${error_count} artifact(s)`);
												}
												cur_list.refresh();
												d.hide();
											}
										}
									});
								});
							}
						});
						d.show();
					}
				}
			];
		}
		return [];
	}
};

frappe.ui.form.on("AI Generated Artifact", {
	refresh(frm) {
		// Add approval buttons for System Managers when status is draft
		if (frm.doc.status === "draft" && frappe.user.has_role("System Manager")) {
			frm.add_custom_button(__("Approve"), function() {
				frappe.confirm(
					__("Are you sure you want to approve this artifact? This will create the DocType."),
					function() {
						frappe.call({
							method: "frappe_ai_form_builder.api.generator.approve_artifact",
							args: {
								artifact_id: frm.doc.name
							},
							callback: function(r) {
								if (r.message) {
									frappe.msgprint(__("Artifact approved successfully!"));
									frm.reload_doc();
								}
							}
						});
					}
				);
			}, __("Actions"));

			frm.add_custom_button(__("Reject"), function() {
				let d = new frappe.ui.Dialog({
					title: __("Reject Artifact"),
					fields: [
						{
							fieldname: "reason",
							fieldtype: "Text",
							label: __("Rejection Reason"),
							reqd: 1
						}
					],
					primary_action_label: __("Reject"),
					primary_action: function(values) {
						frappe.call({
							method: "frappe_ai_form_builder.api.generator.reject_artifact",
							args: {
								artifact_id: frm.doc.name,
								reason: values.reason
							},
							callback: function(r) {
								if (r.message) {
									frappe.msgprint(__("Artifact rejected"));
									frm.reload_doc();
								}
							}
						});
						d.hide();
					}
				});
				d.show();
			}, __("Actions"));
		}

		// Show content preview for draft artifacts
		if (frm.doc.status === "draft" && frm.doc.content) {
			frm.add_custom_button(__("Preview Specification"), function() {
				let d = new frappe.ui.Dialog({
					title: __("JSON Specification Preview"),
					fields: [
						{
							fieldname: "content",
							fieldtype: "Code",
							label: __("Content"),
							options: "JSON",
							default: frm.doc.content,
							read_only: 1
						}
					],
					size: "large"
				});
				d.show();
			});
		}
	}
});

// Initialize global functions for list view buttons
$(document).ready(function() {
	window.approve_artifact = function(artifact_id) {
		frappe.confirm(
			__("Are you sure you want to approve this artifact? This will create the DocType."),
			function() {
				frappe.call({
					method: "frappe_ai_form_builder.api.generator.approve_artifact",
					args: {
						artifact_id: artifact_id
					},
					callback: function(r) {
						if (r.message) {
							frappe.msgprint(__("Artifact approved successfully!"));
							cur_list && cur_list.refresh();
						}
					}
				});
			}
		);
	};

	window.reject_artifact = function(artifact_id) {
		let d = new frappe.ui.Dialog({
			title: __("Reject Artifact"),
			fields: [
				{
					fieldname: "reason",
					fieldtype: "Text",
					label: __("Rejection Reason"),
					reqd: 1
				}
			],
			primary_action_label: __("Reject"),
			primary_action: function(values) {
				frappe.call({
					method: "frappe_ai_form_builder.api.generator.reject_artifact",
					args: {
						artifact_id: artifact_id,
						reason: values.reason
					},
					callback: function(r) {
						if (r.message) {
							frappe.msgprint(__("Artifact rejected"));
							cur_list && cur_list.refresh();
							d.hide();
						}
					}
				});
			}
		});
		d.show();
	};
});
