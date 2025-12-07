# Frappe AI Form Builder - Architecture Documentation

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Interface                          │
│  ┌──────────────────────┐    ┌──────────────────────┐          │
│  │   Chat Widget        │    │   Form Preview       │          │
│  │  (JavaScript/Vue)    │    │    (Live Render)     │          │
│  └──────────┬───────────┘    └──────────┬───────────┘          │
└─────────────┼──────────────────────────┼──────────────────────┘
              │                           │
              └───────────┬───────────────┘
                          │
┌─────────────────────────▼─────────────────────────────────────┐
│                      API Layer (Python)                       │
│  ┌────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │  Session   │  │  Generator   │  │ LLM Adapter  │         │
│  │ Management │  │   (DocType)  │  │ (OpenAI/etc) │         │
│  └─────┬──────┘  └──────┬───────┘  └──────┬───────┘         │
└────────┼─────────────────┼──────────────────┼────────────────┘
         │                 │                  │
         └────────┬────────┴────────┬─────────┘
                  │                 │
┌─────────────────▼─────────────────▼─────────────────────────┐
│                   Business Logic                            │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐      │
│  │  Validator   │  │  Audit Log   │  │  Security   │      │
│  │   Module     │  │    Module    │  │   Checks    │      │
│  └──────────────┘  └──────────────┘  └─────────────┘      │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                    Data Layer                               │
│  ┌────────────┐  ┌────────────┐  ┌──────────────┐         │
│  │    AI      │  │ Generated  │  │  AI Audit    │         │
│  │Conversation│  │  Artifact  │  │     Log      │         │
│  └────────────┘  └────────────┘  └──────────────┘         │
│           (Frappe DocTypes in MariaDB)                     │
└────────────────────────────────────────────────────────────┘
```

## Data Flow

### 1. Session Start
```
User → UI → API.start_session() → Create AI Conversation → Return session_id
```

### 2. Message Exchange
```
User Message → API.send_message() → 
  ├─ Add to Conversation History
  ├─ Call LLM API (OpenAI/Anthropic)
  ├─ Parse Response
  ├─ Validate Schema
  └─ Return AI Response + Draft Spec
```

### 3. DocType Generation
```
Generate Request → API.generate_doctype() →
  ├─ Validate Specification
  ├─ Create AI Generated Artifact (Draft)
  ├─ [Optional] Create Actual DocType
  ├─ Log Audit Trail
  └─ Return Artifact ID
```

### 4. Admin Approval
```
Admin Review → API.approve_artifact() →
  ├─ Check Permissions
  ├─ Create Frappe DocType
  ├─ Update Artifact Status
  ├─ Log Approval
  └─ Return DocType Name
```

## Component Details

### Frontend Components

#### Chat Widget (`frappe_ai_form_builder.js`)
- **Responsibilities**:
  - Render chat interface
  - Manage conversation state
  - Send/receive messages
  - Display typing indicators
  
- **Key Functions**:
  - `start_conversation(template)`: Initialize session
  - `add_message(role, content)`: Add message to UI
  - `update_form_preview(spec)`: Render form preview

#### Form Preview
- **Responsibilities**:
  - Live rendering of DocType spec
  - Show field types, validations
  - Interactive preview
  
- **Features**:
  - Real-time updates
  - Field type visualization
  - Mandatory field indicators

### Backend Components

#### Session Manager (`api/session.py`)
- **Endpoints**:
  - `start_session(template)`: Create new conversation
  - `send_message(session_id, message)`: Process user input
  - `get_session_history(session_id)`: Retrieve history
  - `end_session(session_id)`: Close conversation

#### LLM Adapter (`api/llm_adapter.py`)
- **Responsibilities**:
  - Interface with LLM providers
  - Prompt engineering
  - Response parsing
  - Schema validation

- **Providers**:
  - OpenAI GPT-4
  - Anthropic Claude
  - Extensible for others

#### Generator (`api/generator.py`)
- **Endpoints**:
  - `generate_doctype(session_id, publish)`: Create DocType
  - `approve_artifact(artifact_id)`: Admin approval
  - `reject_artifact(artifact_id, reason)`: Admin rejection

## DocType Schemas

### AI Conversation
```
- user: Link to User
- template: Select (employee_onboarding, etc.)
- state: Select (active, completed, abandoned)
- conversation_history: JSON array
- draft_specification: JSON object
- created_at: Datetime
```

### AI Generated Artifact
```
- artifact_type: Select (DocType, Print Format, etc.)
- artifact_name: String
- content: JSON specification
- status: Select (draft, approved, rejected)
- session_id: Link to AI Conversation
- frappe_doctype: String (actual DocType name)
- created_by: Link to User
- approved_by: Link to User
- rejection_reason: Text
```

### AI Audit Log
```
- action: Select (generate, approve, reject, rollback)
- artifact_id: Link to AI Generated Artifact
- artifact_name: String
- actor: Link to User
- reason: Text
- timestamp: Datetime
```

### AI Config
```
- llm_provider: Select (openai, anthropic)
- openai_model: Select (gpt-4, etc.)
- anthropic_model: Select (claude-3-sonnet, etc.)
- allowed_fieldtypes: Text (multiline)
- blacklisted_fields: Text (multiline)
- auto_approval_enabled: Check
- rate_limit_per_hour: Int
```

## Security Architecture

### Input Validation
1. **Sanitization**: All user inputs sanitized before LLM
2. **Field Name Validation**: Check against regex patterns
3. **Reserved Names**: Block Frappe reserved fields
4. **PII Detection**: Prevent sensitive field creation

### Permission Model
```
System Manager:
  - Full access to all features
  - Can approve/reject artifacts
  - Configure settings

User:
  - Create conversations
  - Generate drafts
  - View own conversations
```

### Audit Trail
- Every AI generation logged
- Admin actions tracked
- Immutable audit records
- Timestamps and actors recorded

## LLM Integration

### System Prompt Structure
```python
"""
You are an expert AI assistant for Frappe Framework...

[Rules]
- Ask clarifying questions
- Validate field names
- Use Frappe field types
- Generate valid JSON

[Output Format]
{
  "doctype_name": "...",
  "fields": [...],
  ...
}
"""
```

### Validation Pipeline
```
LLM Response →
  ├─ Extract JSON from markdown
  ├─ Parse JSON
  ├─ Validate Required Fields
  ├─ Check Field Names (snake_case, no reserved)
  ├─ Validate Field Types
  ├─ Check Link field options
  └─ Return Errors or Success
```

## Deployment Architecture

### Development
```
frappe-bench/
  apps/
    frappe_ai_form_builder/
  sites/
    development.local/
```

### Production
```
- Multi-tenant support
- Site-specific configs
- Separate LLM API keys per site
- Rate limiting per site
```

## Performance Considerations

### Caching Strategy
- Cache LLM responses for identical prompts
- TTL: 24 hours
- Cache key: Hash(conversation_history + message)

### Async Processing
- Long-running generations use background jobs
- Queue: `frappe.enqueue()`
- Timeout: 5 minutes max

### Rate Limiting
- Per-user: 50 requests/hour
- Per-site: 500 requests/hour
- Configurable in AI Config

## Testing Strategy

### Unit Tests
```python
# Test field validation
test_validate_fieldname()
test_validate_fieldtype()
test_reserved_names()

# Test LLM parsing
test_parse_json_response()
test_extract_spec()

# Test DocType creation
test_create_doctype_from_spec()
```

### Integration Tests
```python
# Full flow tests
test_conversation_to_doctype()
test_approval_workflow()
test_rejection_workflow()
```

### End-to-End Tests
- Test complete user journeys
- Validate UI interactions
- Check actual DocType creation

## Error Handling

### User-Facing Errors
- Clear, actionable messages
- No technical details exposed
- Suggest fixes when possible

### Internal Logging
```python
frappe.log_error(
    frappe.get_traceback(),
    "AI Form Builder - Component Error"
)
```

## Monitoring & Metrics

### Key Metrics
- **Time to First Form**: Median generation time
- **Accuracy**: % accepted without changes
- **Error Rate**: % of failed generations
- **API Costs**: LLM token usage

### Dashboards
- Real-time conversation stats
- Approval/rejection rates
- Popular templates
- Error frequency

## Future Enhancements

### Phase 2
- Multi-language support
- Custom prompts per organization
- Batch generation
- Import/export templates

### Phase 3
- Workflow generation
- Permission matrix builder
- Report generation
- Dashboard creation

### Phase 4
- Visual form builder integration
- Voice interface
- Mobile app
- Slack/Teams integration

---

**Last Updated**: December 5, 2025
