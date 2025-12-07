# Frappe AI Form Builder

[![GitHub Repo](https://img.shields.io/badge/GitHub-aman--justin/frappe--ai-blue)](https://github.com/aman-justin/frappe-ai)

AI-powered form and template generator for Frappe Framework. Enables non-technical users to create DocTypes (forms) through conversational AI.

## 🎥 Demo

> **Video coming soon!** Watch a 2-minute walkthrough of creating forms with AI.

<!-- Uncomment when video is ready:
[![AI Form Builder Demo](https://img.youtube.com/vi/YOUR_VIDEO_ID/maxresdefault.jpg)](https://www.youtube.com/watch?v=YOUR_VIDEO_ID)
-->

### Screenshots

![AI Form Builder Interface](https://via.placeholder.com/800x400/4A90E2/ffffff?text=AI+Form+Builder+Interface)
*Conversational interface with live preview*

![Live Form Preview](https://via.placeholder.com/800x400/7B68EE/ffffff?text=Real-Time+Form+Preview)
*See your form being built in real-time*

![Admin Approval](https://via.placeholder.com/800x400/50C878/ffffff?text=Admin+Approval+System)
*Review and approve AI-generated forms*

---

## Features

- 🤖 **Conversational AI Interface**: Chat with AI to describe your form requirements
- 📝 **Automatic DocType Generation**: AI creates complete Frappe forms with fields, validations, and relationships
- 👁️ **Live Preview**: See your form as it's being built
- ✅ **Admin Review System**: Approve or reject AI-generated artifacts before deployment
- 🔒 **Security & Validation**: Built-in safety checks for AI-generated code
- 📊 **Audit Logs**: Track all AI generations and approvals
- 🔄 **Rollback Feature**: Undo changes and experiment freely
- 🧹 **Clear Chat**: Start fresh conversations anytime

## 🚀 Quick Start (TL;DR)

> **⚠️ Note**: Docker setup is not ready yet. Please use the manual setup below.

### Manual Setup (Currently Working ✅)

**Prerequisites**: Python 3.12, Node.js, MariaDB/MySQL, Redis

```bash
# 1. Install Frappe Bench
pip install frappe-bench

# 2. Initialize bench and install Frappe
bench init frappe-bench --frappe-branch version-15
cd frappe-bench

# 3. Get the AI Form Builder app
bench get-app https://github.com/aman-justin/frappe-ai.git

# 4. Create a new site
bench new-site dev.local

# 5. Install and start
bench --site dev.local install-app frappe_ai_form_builder
bench start
```

Visit `http://dev.local:8000/app/ai-form-builder` and start chatting with AI!

### Option 2: Docker (In Progress 🔄)

**Prerequisites**: Install [Docker Desktop](https://www.docker.com/products/docker-desktop)

```bash
# 1. Clone the repository
git clone https://github.com/aman-justin/frappe-ai.git
cd frappe-ai/apps/frappe_ai_form_builder

# 2. Start with Docker (work in progress)
docker compose up -d

# 3. Access the application
```

> **⚠️ Docker Note**: Docker setup is currently under development and not ready for use. Please follow the manual setup instructions below.

---

### Using This Pre-Configured Repository

This repository contains a **complete Frappe bench** with AI Form Builder pre-installed!

```bash
# 1. Clone the repository
git clone https://github.com/aman-justin/frappe-ai.git
cd frappe-ai

# 2. Activate environment & install dependencies
source env/bin/activate
pip install -r apps/frappe/requirements.txt
pip install -r apps/frappe_ai_form_builder/requirements.txt

# 3. Start Redis services
redis-server config/redis_cache.conf &
redis-server config/redis_queue.conf &

# 4. Build assets & start server
bench build
bench start
```

Then configure your API key at **Setup > AI Config** and start building forms!

---

## Prerequisites

Before you begin, ensure you have the following installed on your system:

- **Python 3.10+**: Required for Frappe Framework
- **Node.js 18+**: Required for frontend assets
- **Redis**: For caching and queue management
- **MariaDB/MySQL**: Database server
- **Git**: For cloning repositories

### Installing Prerequisites (Ubuntu/Debian)

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and pip
sudo apt install python3 python3-pip python3-dev python3-venv -y

# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install Redis
sudo apt install redis-server -y

# Install MariaDB
sudo apt install mariadb-server mariadb-client -y
sudo systemctl start mariadb
sudo systemctl enable mariadb

# Secure MariaDB (run and follow prompts)
sudo mysql_secure_installation

# Install Git
sudo apt install git -y

# Install wkhtmltopdf (for PDF generation)
sudo apt install wkhtmltopdf -y
```

### Installing Prerequisites (macOS)

```bash
# Install Homebrew if not installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python
brew install python@3.10

# Install Node.js
brew install node@18

# Install Redis
brew install redis

# Install MariaDB
brew install mariadb
brew services start mariadb

# Secure MariaDB
mysql_secure_installation

# Install Git
brew install git

# Install wkhtmltopdf
brew install wkhtmltopdf
```

## Step-by-Step Installation Guide

This repository contains a **complete pre-configured Frappe bench** with the AI Form Builder app already set up. No need to initialize a new bench or install apps separately!

### Step 1: Clone the Repository

Clone this entire bench repository to your local machine.

```bash
# Clone the complete bench
git clone https://github.com/aman-justin/frappe-ai.git

# Change to the bench directory
cd frappe-ai
```

### Step 2: Set Up Python Virtual Environment

The bench comes with environment configuration, but you need to activate it.

```bash
# Activate the virtual environment
source env/bin/activate

# Install/update Python dependencies
pip install -r apps/frappe/requirements.txt
pip install -r apps/frappe_ai_form_builder/requirements.txt
```

### Step 3: Configure Your Site

The bench includes a pre-configured site. Update the database credentials if needed.

```bash
# Create a new site (or use existing dev.local)
bench new-site your-site.local

# Set the site as default
bench use your-site.local
```

**Note:** If you want to use the existing `dev.local` site, you'll need to:
- Restore the database (if shared)
- Or migrate: `bench --site dev.local migrate`

### Step 4: Install the App (if using a new site)

If you created a new site, install the app:

```bash
# Install the AI Form Builder app
bench --site your-site.local install-app frappe_ai_form_builder
```

### Step 5: Start Redis Services

The bench requires Redis for caching and queue management.

```bash
# Start Redis cache (in background)
redis-server config/redis_cache.conf &

# Start Redis queue (in background)
redis-server config/redis_queue.conf &
```

### Step 6: Build Frontend Assets

Build the JavaScript and CSS assets for the applications.

```bash
# Build all assets
bench build

# Or build specifically for the AI Form Builder
bench build --app frappe_ai_form_builder
```

### Step 7: Start the Development Server

```bash
# Start the bench (this starts all services)
bench start
```

The server will start on `http://localhost:8000` by default.

> **Note:** Get an API key before configuring:
> - **Google Gemini** (Recommended - Free tier): https://aistudio.google.com/app/apikey
> - **OpenAI** (GPT-4): https://platform.openai.com/api-keys
> - **Anthropic** (Claude): https://console.anthropic.com/account/keys

### Step 8: Configure API Key (Web Interface)

1. Open your browser and go to `http://my-site.local:8000` (or `http://localhost:8000` if using default)
2. Log in with the administrator credentials you set during site creation
3. Navigate to **Setup > AI Config** (or search for "AI Config" in the Awesome Bar)
4. Configure your AI provider:
   - **LLM Provider**: Select your preferred provider (Gemini, OpenAI, or Anthropic)
   - **API Key**: Enter your API key in the corresponding field:
     - For Gemini: Enter in "Gemini API Key" field
     - For OpenAI: Enter in "OpenAI API Key" field
     - For Anthropic: Enter in "Anthropic API Key" field
   - **Model**: Select your preferred model (default is selected automatically)
   - **System Prompt**: (Optional) Customize the AI behavior
5. Click **Save** to store your configuration

### Step 9: Access the AI Form Builder Workspace

After logging in, you'll see the **AI Form Builder** workspace automatically available:

1. **From Sidebar**: Look for the AI Form Builder icon (🤖) in the left sidebar
2. **From Workspace Menu**: Click the grid icon at the top-left and select "AI Form Builder"
3. **From Search**: Press `Ctrl+K` (or `Cmd+K` on Mac) and search for "AI Form Builder"

The workspace includes shortcuts to:
- **AI Conversation**: View conversation history
- **AI Generated Artifact**: Review and approve generated forms
- **AI Config**: Configure API keys and settings
- **AI Audit Log**: Track all AI operations

### Step 10: Start Building Forms

1. **Access the Form Builder**:
   - Click the "form-builder" link in the AI Form Builder sidebar
   - OR navigate directly to: `http://localhost:8000/ai_form_builder`

2. **Choose Your Approach**:
   - **Quick Start**: Select from predefined templates:
     - 👥 Human Resources (Employee Onboarding, Performance Review, etc.)
     - 🎯 Customer Relationship (Lead Capture, Feedback, etc.)
     - 📦 Inventory Management (Product Entry, Stock Request, etc.)
     - 📋 Project Management (Task, Milestone, etc.)
   - **Custom Prompt**: Type your own requirement in the custom input box

3. **Build Your Form**:
   - Have a conversation with the AI about your form requirements
   - Answer questions about fields, validations, and relationships
   - Watch the **Live Preview** update in real-time on the right panel

4. **Create the Form**:
   - When satisfied with the preview, click the **✨ Create Form** button
   - The form will be created as a draft

5. **Approve the Form** (Admin only):
   - Navigate to **AI Generated Artifact** from the workspace
   - Review the generated DocType specification
   - Click **Approve** to activate the form in your system
   - OR click **Reject** to discard it

### Step 11: Using the Rollback Feature

The AI Form Builder includes a powerful rollback feature:

- **Hover over your messages** to see the rollback button (↶)
- **Click the rollback button** to restore the conversation and form to that point
- The rollback counter shows how many states you can go back to
- **Use the "Clear Chat" button** in the header to start a fresh conversation
- **Use the "Create New Form" button** to start building a new form after successful creation

This allows you to experiment freely and undo changes without starting over!

## Quick Start Guide

Once everything is set up:

1. **Open AI Form Builder**: Navigate to the AI Form Builder page from the workspace
2. **Choose a Template or Custom Prompt**: 
   - Select from predefined templates (HR, CRM, Inventory, etc.)
   - OR type your own custom requirement
3. **Describe Your Form**: Tell the AI what kind of form you need (e.g., "Create an employee onboarding form")
4. **Answer Questions**: The AI will ask for details about fields, validations, etc.
5. **Review Live Preview**: See your form being built in real-time on the right panel
6. **Create Form**: Click the **✨ Create Form** button when satisfied
7. **Admin Approval**: An administrator must approve the generated form before it becomes active

## Usage Example

```
AI: What form would you like to create?
You: I need an employee onboarding form

AI: What fields do you need in the Employee Onboarding form?
You: Employee Name, Email, Start Date, Department (link to Department),
     Manager (link to Employee), and Resume attachment

AI: Should any of these fields be mandatory?
You: Yes, make Employee Name, Email, and Start Date mandatory

AI: Here's a preview of your form. Would you like to make any changes?
You: Looks good!

[The "✨ Create Form" button appears]

AI: Your form specification is ready! Click the "Create Form" button to generate it.
     An admin will review it before activation.
```

## Configuration Options

### AI Config Settings

Access AI configuration at **Setup > AI Config**:

- **LLM Provider**: Choose between Gemini, OpenAI, or Anthropic
- **API Keys**: Configure your API key for the selected provider
  - **Gemini API Key**: For Google Gemini (get from https://aistudio.google.com/app/apikey)
  - **OpenAI API Key**: For OpenAI GPT models (get from https://platform.openai.com/api-keys)
  - **Anthropic API Key**: For Anthropic Claude (get from https://console.anthropic.com/account/keys)
- **Model Selection**: Choose specific model version:
  - **Gemini**: gemini-3-pro, gemini-2.5-pro, gemini-2.5-flash, gemini-2.5-flash-lite
  - **OpenAI**: gpt-4, gpt-4-turbo, gpt-3.5-turbo
  - **Anthropic**: claude-3-opus, claude-3-sonnet, claude-3-haiku
- **System Prompt**: Customize how the AI behaves and responds
- **Allowed Field Types**: Restrict which Frappe field types AI can use
- **Blacklisted Fields**: Prevent certain field names for security (e.g., password, api_key)
- **Auto Approval**: Enable/disable automatic approval for low-risk changes
- **Rate Limit**: Control API usage per hour (default: 100)

## Troubleshooting

### Common Issues

#### Bench Start Fails
```bash
# Check Redis is running
redis-cli ping

# Check MariaDB is running
sudo systemctl status mariadb

# Clear cache and try again
bench clear-cache
bench start
```

#### App Installation Fails
```bash
# Check for missing dependencies
bench --site my-site.local install

# Rebuild assets
bench build
```

#### AI Not Responding
1. **Check API Key Configuration**:
   - Go to **Setup > AI Config**
   - Verify your API key is entered correctly
   - Make sure there are no extra spaces
   - Try regenerating your API key from the provider's website

2. **Verify Provider Selection**:
   - Ensure the correct LLM Provider is selected (Gemini, OpenAI, or Anthropic)
   - The API key field should match the selected provider

3. **Test API Connection**:
   ```bash
   # For Gemini
   curl "https://generativelanguage.googleapis.com/v1beta/models?key=YOUR_API_KEY"
   
   # For OpenAI
   curl -H "Authorization: Bearer YOUR_API_KEY" https://api.openai.com/v1/models
   
   # For Anthropic
   curl -H "x-api-key: YOUR_API_KEY" https://api.anthropic.com/v1/messages
   ```

4. **Check Rate Limits**: Verify you haven't exceeded your API provider's rate limits

#### Database Connection Issues
```bash
# Check MariaDB credentials
bench --site my-site.local config get db_name
bench --site my-site.local config get db_password

# Test database connection
bench --site my-site.local mariadb
```

#### Permission Errors
```bash
# Fix file permissions
sudo chown -R $USER:$USER /path/to/your/bench

# Fix Redis permissions if needed
sudo chown redis:redis /var/lib/redis
```

### Logs and Debugging

```bash
# View bench logs
bench logs

# View site-specific logs
tail -f sites/my-site.local/logs/frappe.log

# Enable debug mode
bench --site my-site.local set-config developer_mode 1
```

## Development

### Project Structure
```
frappe_ai_form_builder/
├── frappe_ai_form_builder/
│   ├── api/
│   │   ├── session.py          # Session management
│   │   ├── generator.py        # DocType generation
│   │   └── llm_adapter.py      # LLM integration
│   ├── public/
│   │   ├── js/                 # Frontend JavaScript
│   │   └── css/                # Styles
│   ├── www/
│   │   └── ai_form_builder.html # Main UI
│   ├── ai_conversation/        # Conversation DocType
│   ├── ai_generated_artifact/  # Generated artifacts DocType
│   └── hooks.py                # Frappe hooks
├── setup.py
├── requirements.txt
└── pyproject.toml
```

### Running Tests
```bash
# Run all tests
bench --site my-site.local run-tests --app frappe_ai_form_builder

# Run specific test
bench --site my-site.local run-tests --app frappe_ai_form_builder --test test_session.py
```

### Development Mode
```bash
# Enable developer mode
bench --site my-site.local set-config developer_mode 1

# Start with auto-reload
bench start --dev
```

### Making Changes
```bash
# Pull latest changes
cd apps/frappe_ai_form_builder
git pull origin main

# Make your changes
# ...

# Migrate database if needed
bench --site my-site.local migrate

# Build assets
bench build
```

## API Reference

### Start Session
```python
POST /api/method/frappe_ai_form_builder.api.session.start_session
Response: {"session_id": "abc123"}
```

### Send Message
```python
POST /api/method/frappe_ai_form_builder.api.session.send_message
{
    "session_id": "abc123",
    "message": "Create an employee form"
}
```

### Generate DocType
```python
POST /api/method/frappe_ai_form_builder.api.generator.generate_doctype
{
    "session_id": "abc123",
    "publish": false
}
```

## Security

- All AI-generated code requires admin approval
- Input validation prevents malicious code injection
- Rate limiting protects against abuse
- Audit logs track all activities
- PII detection and field blacklisting

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make changes with tests
4. Submit a pull request

## License

MIT License

## Support

- Issues: [GitHub Issues](https://github.com/aman-justin/frappe-ai/issues)
- Discussions: [GitHub Discussions](https://github.com/aman-justin/frappe-ai/discussions)
- Documentation: [Frappe Framework Docs](https://frappeframework.com/docs)

---

**Built for the Frappe Framework with ❤️**
