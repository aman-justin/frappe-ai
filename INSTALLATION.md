# Installation & Setup Guide

## Prerequisites

- Frappe Framework (v14 or v15)
- Python 3.10+
- MariaDB
- Node.js 16+
- OpenAI or Anthropic API key

## Quick Start

### 1. Install the App

```bash
# Navigate to your Frappe bench
cd frappe-bench

# Get the app
bench get-app https://github.com/yourusername/frappe_ai_form_builder.git

# Install on your site
bench --site your-site-name install-app frappe_ai_form_builder

# Migrate database
bench --site your-site-name migrate
```

### 2. Configure LLM Provider

#### Option A: OpenAI

```bash
# Add API key to site config
bench --site your-site-name set-config openai_api_key "sk-..."

# Or edit sites/your-site-name/site_config.json
{
  "openai_api_key": "sk-..."
}
```

#### Option B: Anthropic Claude

```bash
# Add API key to site config
bench --site your-site-name set-config anthropic_api_key "sk-ant-..."
```

### 3. Configure Settings

1. Login to your site
2. Go to **Setup > AI Config**
3. Select your LLM provider (OpenAI or Anthropic)
4. Configure allowed field types
5. Set blacklisted fields (PII protection)
6. Adjust rate limits

### 4. Start Using

1. Click **Tools > AI Form Builder** in the top menu
2. Start a conversation
3. Describe your form requirements
4. Generate your DocType!

## Development Setup

### Local Development

```bash
# Clone the repository
git clone https://github.com/yourusername/frappe_ai_form_builder.git
cd frappe_ai_form_builder

# Install dependencies
pip install -r requirements.txt

# Create a new bench (if needed)
bench init frappe-bench --frappe-branch version-15
cd frappe-bench

# Add the app
bench get-app /path/to/frappe_ai_form_builder

# Create a site
bench new-site development.local
bench --site development.local install-app frappe_ai_form_builder

# Start development server
bench start
```

### Enable Developer Mode

```bash
# Enable developer mode
bench --site development.local set-config developer_mode 1

# Clear cache after changes
bench --site development.local clear-cache
```

### Watch for Changes

```bash
# In one terminal: watch Python changes
bench --site development.local watch

# In another terminal: watch JS/CSS changes
cd apps/frappe_ai_form_builder
npm run watch
```

## Configuration Options

### AI Config (Single DocType)

Access via: **Setup > AI Config**

- **LLM Provider**: Choose OpenAI or Anthropic
- **Model Selection**: Pick specific model version
- **Allowed Field Types**: Control which Frappe field types can be used
- **Blacklisted Fields**: Prevent creation of sensitive fields
- **Auto Approval**: Enable automatic approval for low-risk changes
- **Rate Limiting**: Set API call limits per hour

### Site Config (`site_config.json`)

```json
{
  "openai_api_key": "sk-...",
  "anthropic_api_key": "sk-ant-...",
  "rate_limit_enabled": true,
  "rate_limit_per_hour": 100
}
```

## Permissions Setup

### Default Roles

**System Manager**:
- Full access to all features
- Can approve/reject artifacts
- Configure AI settings
- View all conversations

**User**:
- Create conversations
- Generate draft DocTypes
- View own conversations

### Custom Permissions

1. Go to **Setup > Role Permissions Manager**
2. Select "AI Generated Artifact"
3. Customize who can approve/reject

## Troubleshooting

### LLM API Not Working

```bash
# Check if API key is configured
bench --site your-site-name console
>>> import frappe
>>> frappe.conf.get("openai_api_key")

# Test API connection
>>> from frappe_ai_form_builder.api.llm_adapter import get_openai_response
>>> get_openai_response([], "Hello")
```

### Chat UI Not Loading

```bash
# Clear cache
bench --site your-site-name clear-cache

# Rebuild assets
bench build --app frappe_ai_form_builder

# Check browser console for JavaScript errors
# Open DevTools > Console
```

### Import Errors

```bash
# Reinstall dependencies
pip install -r requirements.txt --upgrade

# Restart bench
bench restart
```

### DocType Creation Fails

1. Check validation errors in **AI Audit Log**
2. Review field naming rules (lowercase, underscores)
3. Ensure Link fields reference existing DocTypes
4. Check for reserved field names

## Upgrading

```bash
# Get latest version
cd frappe-bench/apps/frappe_ai_form_builder
git pull origin main

# Migrate database
bench --site your-site-name migrate

# Clear cache and restart
bench --site your-site-name clear-cache
bench restart
```

## Uninstalling

```bash
# Uninstall from site
bench --site your-site-name uninstall-app frappe_ai_form_builder

# Remove app files (optional)
bench remove-app frappe_ai_form_builder
```

## Production Deployment

### Using Nginx

```nginx
# Add to your nginx config
location /assets/frappe_ai_form_builder {
    alias /path/to/frappe-bench/sites/assets/frappe_ai_form_builder;
}
```

### Environment Variables

```bash
# Set in production environment
export OPENAI_API_KEY="sk-..."
export RATE_LIMIT_PER_HOUR=500
```

### Monitoring

```bash
# Enable error logging
bench --site your-site-name set-config error_log_file "/var/log/frappe/error.log"

# Monitor LLM usage
# Check AI Audit Log for API call statistics
```

## Common Issues

### Issue: "OpenAI API key not configured"
**Solution**: Set API key in site_config.json

### Issue: "Insufficient permissions"
**Solution**: Add user to System Manager role or configure custom permissions

### Issue: "Rate limit exceeded"
**Solution**: Adjust rate_limit_per_hour in AI Config

### Issue: "Failed to generate DocType"
**Solution**: Check validation errors in AI Audit Log, ensure field names are valid

## Getting Help

- **Documentation**: [Link to docs]
- **GitHub Issues**: [Link to issues]
- **Community Forum**: [Link to forum]
- **Email Support**: your.email@example.com

---

**Need help with your interview project?** Feel free to reach out!
