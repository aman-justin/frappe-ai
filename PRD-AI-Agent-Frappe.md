# PRD: AI Guided Form & Template Generator for Frappe

## Overview
Build an AI agent integrated into Frappe that interactively asks clients a configurable set of questions, infers the required data model, and generates:
- DocTypes (forms) with fields, validations, links, and properties
- Print/email templates and sample records
- Optional workflows, role/permission configs, and sample reports

Target: speed up onboarding of custom forms and templates for non-technical users while producing high-quality, production-ready Frappe artifacts.

Repo: frappe/frappe (integration points and app packaging should follow Frappe app conventions).

## Goals
- Primary: Enable non-technical users to create new DocTypes and templates by conversing with an AI agent.
- Secondary: Provide an approval/review flow for administrators to vet AI-created artifacts before activation.
- Keep generated artifacts as native Frappe DocTypes/templates so they can be edited manually after generation.

## Success Metrics
- Time-to-first-form: median time for a user to generate a usable DocType < 10 minutes.
- Accuracy: ≥ 85% of generated DocTypes accepted by admin with ≤ 2 adjustments.
- Adoption: 20% of new small-customers (pilot) use the agent for initial setup in 3 months.
- Quality: Fewer than 5% severe bugs originating from auto-generated artifacts in first 6 months.

## Non-Goals
- Replace professional developer workflows for very complex models.
- Build a complete LLM service—will integrate with chosen LLM provider(s).

## Users & Personas
- Non-technical customer/HR: Wants new form for onboarding, leave requests, etc.
- Business analyst: Defines fields and validations but prefers guided UI.
- Admin/Developer: Reviews, changes, approves generated DocTypes.
- System integrator: Wants programmatic control (APIs) for automation.

## High-Level User Flows

1. User starts an "AI Form Builder" session from Desk or Setup.
2. AI greets and asks a short series of adaptive questions (purpose, entities, fields, relationships, permissions, workflows).
3. AI proposes a draft DocType specification and a preview form.
4. User refines via chat (add/remove fields, change types, set validations).
5. User chooses to "Generate" or "Create Draft".
6. System creates:
   - New DocType JSON (in Frappe format)
   - Optional Print/Email Template
   - Example record(s)
   - Optional workflow and permission templates
7. Admin reviews and approves/publishes changes (or edit manually) before enabling on production.

## Key Features

1. Conversational Agent (Chat UI)
   - Stateful conversation per session (saves in Conversation DocType).
   - Adaptive Q: asks clarifying questions as needed.
   - Pre-built question flows (onboarding form, invoice, support ticket, etc.)
   - Undo / Rollback and "Explain why" for each generated field.

2. DocType Generator
   - Map AI response to Frappe DocType JSON (fields, fieldtype, options, default, mandatory, validators).
   - Support Link fields, Table (child DocTypes), Select options, Attachments.
   - Automated naming, slugging, help text & labels.

3. Template Generator
   - Generate Print format (Jinja/HTML) templates and email templates.
   - Create sample Jinja snippets for common use.

4. Admin Review & Approval
   - Created artifacts saved as Draft DocTypes and flagged for review.
   - Diff viewer against existing DocTypes.
   - Preview mode with sample data.

5. Integration & API
   - REST endpoints for starting sessions, submitting answers, generating artifacts.
   - Webhook support for embedding into onboarding flows.
   - CLI/scriptable mode for power users.

6. Audit & Rollback
   - Conversation logs, generation diffs, user who approved, timestamps.
   - One-click rollback to previous DocType state.

7. Extensibility & Config
   - Add custom question templates & domain-specific vocabularies.
   - Allow organization admins to set guardrails (deny certain field types, PII flags).

## Data Model (Suggested DocTypes)
- AI Conversation
  - session_id, user, prompts[], responses[], state, created_at
- AI Generated Artifact
  - artifact_id, artifact_type (DocType, PrintFormat), content (JSON), status (draft/approved), created_by, diffs
- AI Audit Log
  - action (generate, approve, rollback), actor, timestamp, reason
- AI Config (per site)
  - allowed_fieldtypes, blacklisted_fields, default_permissions, llm_provider_config

## Technical Design

1. Components
   - Frontend
     - Chat Widget integrated into Desk and Setup pages.
     - Form preview renderer using native Frappe form renderer.
     - Review UI with diff and preview.
   - Backend (Frappe app)
     - app: frappe_ai_form_builder (or similar)
     - Controllers: API endpoints to manage sessions, call LLM, map responses -> DocType.
     - Workers: asynchronous generation, validation, sample data creation.
   - LLM Layer
     - Adapter service to LLM provider(s) (OpenAI, Anthropic, self-hosted LlamaX).
     - Prompt templates and safety filters.
   - Storage
     - Save conversations, drafts, artifacts as native DocTypes in Frappe DB.

2. LLM & Prompting
   - Use system-level prompt with strict schema instructions (output must be JSON adhering to a DocType schema).
   - Chain-of-thought disabled in output (no hallucinated fields without asking).
   - Use "schema-first" approach: the model is asked to output a machine-parseable spec and natural-language explanations.
   - Example expected JSON output:
     {
       "doctype_name": "Employee Onboarding",
       "fields": [
         {"fieldname":"employee_name","label":"Employee Name","fieldtype":"Data","mandatory":true},
         {"fieldname":"start_date","label":"Start Date","fieldtype":"Date","mandatory":true}
       ],
       "print_template":"<html>...</html>"
     }

3. Validation & Safety
   - Validator module checks field types, reserved names, forbidden patterns, PII flags.
   - Schema constraints enforced by backend; any invalid output prompts a follow-up question to the user.
   - Admin approval required for production publishing.

4. Creation Flow (backend)
   - Step A: conversation -> draft specification
   - Step B: specification -> validation & static analysis
   - Step C: specification -> create DocType (as draft) via Frappe API (doctype.save())
   - Step D: create PrintFormat / Email Template using Frappe print format modules
   - Step E: create sample record(s) using generated sample_data

5. Hosting & Scaling
   - LLM calls will be rate-limited and queued.
   - Cache prompt/response for reproducibility.
   - Support multi-tenant configs per site in multi-site Frappe deployments.

## UI/UX Details

- Entry Points
  - New Setup page: "AI Form Builder"
  - Contextual: For an existing DocType, "Enhance with AI" to suggest additions
- Chat Screen
  - Left: conversation; Right: live preview (form)
  - Inline controls: accept field, edit field, delete field, ask follow-up
- Review Screen
  - Side-by-side diff (old vs generated)
  - Approve / Request Changes / Reject
- Admin Settings
  - LLM provider config, cost tracking, allowed fields, PII policy.

## API Sketch (examples)
- POST /api/method/ai_form_builder.start_session
  - payload: {template: "employee_onboarding", user_id}
- POST /api/method/ai_form_builder.respond
  - payload: {session_id, response_text}
- POST /api/method/ai_form_builder/generate
  - payload: {session_id, publish: false}
- GET /api/resource/AI%20Generated%20Artifact/{name}

(Use standard Frappe REST method naming and permission checks.)

## Acceptance Criteria
- Chat UI implemented and can hold stateful conversation sessions.
- AI produces a machine-parseable DocType JSON in at least 90% test cases for predefined templates.
- Generated DocType can be saved as Draft and previewed as a live form.
- Admin review UI shows diffs and allows approve/reject.
- Security controls for PII, with configurable blacklists.
- Audit logs are stored for each generated artifact and publish action.

## Testing Strategy
- Unit tests: mapping functions (AI JSON -> DocType), validators.
- Integration tests: full flow from session start -> generation -> draft creation -> publish.
- End-to-end tests: chat flows for top 10 templates.
- Human-in-the-loop QA: manual review of first 50 generated DocTypes in pilot.


## Example Conversation Flow (abridged)
- Agent: "What is the form for?"
- User: "Employee onboarding"
- Agent: "Which fields do you need? e.g., Name, Email, Start Date, Department"
- User: "Name, Email, Start Date, Department, Manager (link to Employee), Resume (file upload)"
- Agent: "Do any fields need to be mandatory or validated?"
- User: "Name, Email, Start Date mandatory; Email validated"
- Agent: "I propose the following DocType... [shows live preview]. Accept or ask changes?"
- User: "Change Department to link to 'Department' doctype"
- Agent: "Done. Ready to generate draft?"

#