/**
 * Frappe AI Form Builder - Main JavaScript
 */

console.log('🚀 AI Form Builder JavaScript Loaded!');

frappe.provide('frappe_ai_form_builder');

// Initialize AI Form Builder
frappe_ai_form_builder.init = function() {
    console.log('Frappe AI Form Builder initialized');
};

// Start a new AI conversation
frappe_ai_form_builder.start_conversation = function(template) {
    const dialog = new frappe.ui.Dialog({
        title: __('AI Form Builder'),
        size: 'extra-large',
        fields: [
            {
                fieldname: 'chat_area',
                fieldtype: 'HTML'
            }
        ],
        primary_action_label: __('Close'),
        primary_action: function() {
            dialog.hide();
        }
    });
    
    dialog.show();
    
    // Initialize chat interface
    const chat_html = `
        <div class="ai-form-builder-container">
            <div class="chat-section">
                <div class="chat-messages" id="chat-messages"></div>
                <div class="chat-input-area">
                    <textarea 
                        id="user-message" 
                        class="form-control" 
                        placeholder="Type your message here..."
                        rows="3"
                    ></textarea>
                    <button class="btn btn-primary btn-sm mt-2" id="send-message">
                        Send
                    </button>
                </div>
            </div>
            <div class="preview-section">
                <h5>Form Preview</h5>
                <div id="form-preview" class="form-preview-area">
                    <p class="text-muted">Preview will appear here as you build your form...</p>
                </div>
                <div class="preview-actions mt-3" style="display:none;" id="preview-actions">
                    <button class="btn btn-success btn-sm" id="generate-draft">
                        Generate Draft
                    </button>
                    <button class="btn btn-primary btn-sm" id="generate-publish">
                        Generate & Publish
                    </button>
                </div>
            </div>
        </div>
        <style>
            .ai-form-builder-container {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 20px;
                min-height: 500px;
            }
            .chat-section {
                display: flex;
                flex-direction: column;
                border-right: 1px solid #d1d8dd;
                padding-right: 15px;
            }
            .chat-messages {
                flex: 1;
                overflow-y: auto;
                margin-bottom: 15px;
                max-height: 400px;
            }
            .chat-message {
                margin-bottom: 15px;
                padding: 10px;
                border-radius: 8px;
            }
            .chat-message.user {
                background-color: #e8f4fd;
                margin-left: 20px;
            }
            .chat-message.assistant {
                background-color: #f7f9fa;
                margin-right: 20px;
            }
            .chat-message-role {
                font-weight: bold;
                margin-bottom: 5px;
                color: #4a5568;
            }
            .chat-input-area {
                border-top: 1px solid #d1d8dd;
                padding-top: 15px;
            }
            .preview-section {
                padding-left: 15px;
            }
            .form-preview-area {
                border: 1px solid #d1d8dd;
                border-radius: 4px;
                padding: 15px;
                min-height: 350px;
                background-color: #fff;
            }
            .preview-field {
                margin-bottom: 15px;
            }
            .preview-field label {
                font-weight: 600;
                margin-bottom: 5px;
                display: block;
            }
            .preview-field .mandatory {
                color: red;
            }
        </style>
    `;
    
    dialog.fields_dict.chat_area.$wrapper.html(chat_html);
    
    // Start session
    let session_id = null;
    
    frappe.call({
        method: 'frappe_ai_form_builder.api.session.start_session',
        args: { template: template },
        callback: function(r) {
            if (r.message) {
                session_id = r.message.session_id;
                add_message('assistant', r.message.message);
            }
        }
    });
    
    // Send message handler
    dialog.$wrapper.find('#send-message').on('click', function() {
        const message = dialog.$wrapper.find('#user-message').val().trim();
        if (!message) return;
        
        add_message('user', message);
        dialog.$wrapper.find('#user-message').val('');
        
        frappe.call({
            method: 'frappe_ai_form_builder.api.session.send_message',
            args: {
                session_id: session_id,
                message: message
            },
            callback: function(r) {
                if (r.message) {
                    add_message('assistant', r.message.message);
                    
                    // Update preview if draft spec is available
                    if (r.message.draft_spec) {
                        update_form_preview(r.message.draft_spec);
                    }
                    
                    // Show generate buttons if ready
                    if (r.message.ready_to_generate) {
                        dialog.$wrapper.find('#preview-actions').show();
                    }
                }
            }
        });
    });
    
    // Allow Enter to send (Shift+Enter for new line)
    dialog.$wrapper.find('#user-message').on('keydown', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            dialog.$wrapper.find('#send-message').click();
        }
    });
    
    // Generate draft handler
    dialog.$wrapper.find('#generate-draft').on('click', function() {
        generate_doctype(session_id, false);
    });
    
    // Generate and publish handler
    dialog.$wrapper.find('#generate-publish').on('click', function() {
        frappe.confirm(
            __('Are you sure you want to publish this DocType immediately?'),
            function() {
                generate_doctype(session_id, true);
            }
        );
    });
    
    function add_message(role, content) {
        const messages_div = dialog.$wrapper.find('#chat-messages');
        const message_html = `
            <div class="chat-message ${role}">
                <div class="chat-message-role">${role === 'user' ? 'You' : 'AI Assistant'}</div>
                <div class="chat-message-content">${content}</div>
            </div>
        `;
        messages_div.append(message_html);
        messages_div.scrollTop(messages_div[0].scrollHeight);
    }
    
    function update_form_preview(spec) {
        const preview_div = dialog.$wrapper.find('#form-preview');
        let preview_html = `<h6>${spec.doctype_name}</h6>`;
        
        if (spec.description) {
            preview_html += `<p class="text-muted small">${spec.description}</p>`;
        }
        
        preview_html += '<hr>';
        
        spec.fields.forEach(field => {
            preview_html += `
                <div class="preview-field">
                    <label>
                        ${field.label}
                        ${field.mandatory ? '<span class="mandatory">*</span>' : ''}
                    </label>
                    <input 
                        type="text" 
                        class="form-control" 
                        placeholder="${field.fieldtype}"
                        disabled
                    />
                    ${field.description ? `<small class="text-muted">${field.description}</small>` : ''}
                </div>
            `;
        });
        
        preview_div.html(preview_html);
    }
    
    function generate_doctype(session_id, publish) {
        frappe.call({
            method: 'frappe_ai_form_builder.api.generator.generate_doctype',
            args: {
                session_id: session_id,
                publish: publish
            },
            callback: function(r) {
                if (r.message) {
                    // Show success message and artifact information
                    const artifactId = r.message.artifact_id;
                    const doctypeName = r.message.doctype_name;

                    frappe.msgprint({
                        title: __('Success'),
                        message: r.message.message,
                        indicator: 'green'
                    });

                    // If published, navigate to the created DocType
                    if (publish) {
                        dialog.hide();
                        frappe.set_route('Form', 'DocType', doctypeName);
                        return;
                    }

                    // For drafts, offer quick actions (View Draft and Approve & Publish)
                    const result_dialog = new frappe.ui.Dialog({
                        title: __('Artifact Created'),
                        fields: [
                            {fieldname: 'artifact_id', fieldtype: 'Data', label: __('Artifact ID'), default: artifactId, read_only: 1},
                            {fieldname: 'artifact_name', fieldtype: 'Data', label: __('DocType (proposed)'), default: doctypeName, read_only: 1}
                        ],
                        primary_action_label: __('View Draft'),
                        primary_action(values) {
                            result_dialog.hide();
                            // Open the AI Generated Artifact record
                            frappe.set_route('Form', 'AI Generated Artifact', artifactId);
                        },
                        secondary_action_label: __('Approve & Publish'),
                        secondary_action() {
                            result_dialog.hide();
                            // Call approve endpoint
                            frappe.call({
                                method: 'frappe_ai_form_builder.api.generator.approve_artifact',
                                args: { artifact_id: artifactId },
                                callback: function(res) {
                                    if (res.message) {
                                        frappe.msgprint({
                                            title: __('Published'),
                                            message: res.message.message,
                                            indicator: 'green'
                                        });
                                        if (res.message.doctype_name) {
                                            dialog.hide();
                                            frappe.set_route('Form', 'DocType', res.message.doctype_name);
                                        }
                                    }
                                }
                            });
                        }
                    });

                    result_dialog.show();
                }
            }
        });
    }
};

// Add menu item to Desk
frappe.provide('frappe.ui.toolbar');

$(document).on('app_ready', function() {
    frappe_ai_form_builder.init();
    
    // Method 1: Add to awesome bar (search)
    if (frappe.search && frappe.search.utils) {
        frappe.search.utils.make_function_searchable(
            frappe_ai_form_builder.start_conversation,
            __("AI Form Builder")
        );
    }
    
    // Method 2: Add to navbar Tools dropdown
    if (frappe.ui.toolbar.add_dropdown_button) {
        frappe.ui.toolbar.add_dropdown_button('Tools', __('AI Form Builder'), function() {
            frappe_ai_form_builder.start_conversation();
        }, 'fa fa-magic');
    }
    
    // Method 3: Add as a custom toolbar action
    $('.navbar-home').after(`
        <li class="nav-item">
            <a class="nav-link" href="#" onclick="frappe_ai_form_builder.start_conversation(); return false;" 
               title="${__('AI Form Builder')}">
                <svg class="icon icon-sm">
                    <use href="#icon-magic"></use>
                </svg>
                <span class="hidden-xs hidden-sm">${__('AI Form Builder')}</span>
            </a>
        </li>
    `);
    
    console.log('AI Form Builder loaded - Click the AI Form Builder button in toolbar or Tools menu');
});
