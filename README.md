# Jira Loading Progress Monitor

A CrewAI-powered application that monitors Jira sprint boards, verifies story point loading for team members (target: 9 story points per sprint), and automatically generates and sends reports via Microsoft Teams.

## Features

- **Jira Integration**: Connects to Atlassian Jira to retrieve active sprint data
- **Story Point Verification**: Checks that each team member has exactly 9 story points per sprint
- **Automated Reporting**: Generates comprehensive sprint loading reports
- **Teams Integration**: Sends reports directly to specified email addresses via Microsoft Teams

## Agents

### 1. JiraLoading Agent
- Checks sprint board for active sprint
- Verifies story points per team member
- Creates tasks for generating individual reports
- Identifies loading discrepancies

### 2. Reporting Analyst Agent
- Generates detailed sprint loading reports
- Formats reports professionally
- Sends reports via Microsoft Teams to bala.poulami@outlook.com

## Installation

### Prerequisites

- Python >=3.10, <3.14
- Atlassian Jira account with API access
- Microsoft Teams webhook or Graph API credentials

### Setup

1. **Clone or navigate to the project:**
   ```bash
   cd JiraLoadingProgressMonitor
   ```

2. **Install dependencies using uv:**
   ```bash
   uv sync
   ```

   Or using pip:
   ```bash
   pip install -e .
   ```

3. **Configure environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

## Configuration

### Environment Variables (.env)

#### LLM Provider
```env
LLM_PROVIDER=openai  # or ollama, anthropic
OPENAI_API_KEY=your_key_here
```

#### Atlassian Jira
```env
JIRA_URL=https://your-domain.atlassian.net
JIRA_USERNAME=your-email@example.com
JIRA_API_TOKEN=your_api_token
JIRA_PROJECT_KEY=PROJ
```

**Getting Jira API Token:**
1. Go to https://id.atlassian.com/manage-profile/security/api-tokens
2. Create API token
3. Copy token to `.env`

#### Microsoft Teams
```env
# Option 1: Webhook (Easier)
TEAMS_WEBHOOK_URL=https://outlook.office.com/webhook/...

# Option 2: Graph API
MICROSOFT_GRAPH_API_TOKEN=your_token
MICROSOFT_GRAPH_SENDER_EMAIL=sender@example.com

TEAMS_RECIPIENT_EMAIL=bala.poulami@outlook.com
```

**Getting Teams Webhook:**
1. Open your Teams channel
2. Go to Channel options > Connectors
3. Search for "Incoming Webhook"
4. Configure and copy the webhook URL

## Usage

### Run the Monitor

```bash
uv run python -m jira_loading_monitor.main
```

Or using the entry point:
```bash
uv run jira_monitor
```

### Output

The application will:
1. Connect to Jira and retrieve active sprint data
2. Analyze story points per team member
3. Generate a detailed report (`sprint_loading_report.md`)
4. Send the report via Teams to bala.poulami@outlook.com

## MCP Configuration for Atlassian

This project uses MCP (Model Context Protocol) for Atlassian integration. The Atlassian tools are configured in:

- `src/jira_loading_monitor/tools/atlassian_tool.py`

### Available Atlassian Tools

1. **get_active_sprint_board**: Retrieves active sprint board with issues, team members, and story points
2. **get_team_member_sprint_issues**: Gets all issues for a specific team member in the active sprint

### MCP Server Setup

To use the Atlassian MCP server:

1. Install MCP server (if using standalone):
   ```bash
   npm install -g @modelcontextprotocol/server-atlassian
   ```

2. Configure MCP in your environment or use the direct integration via `atlassian-python-api` (already configured in this project).

## Project Structure

```
JiraLoadingProgressMonitor/
├── src/
│   └── jira_loading_monitor/
│       ├── __init__.py
│       ├── main.py
│       ├── crew.py
│       ├── config/
│       │   ├── agents.yaml
│       │   └── tasks.yaml
│       └── tools/
│           ├── __init__.py
│           ├── atlassian_tool.py  # Atlassian MCP tools
│           └── teams_tool.py      # Teams integration
├── pyproject.toml
├── .env.example
├── .gitignore
└── README.md
```

## Troubleshooting

### Jira Connection Issues
- Verify JIRA_URL is correct (include https://)
- Check API token is valid
- Ensure project key matches your Jira project

### Teams Delivery Issues
- Verify webhook URL is active
- Check recipient email format
- Test webhook separately using curl or Postman

### Story Points Not Found
- Jira custom field ID for story points may vary
- Update `customfield_10016` in `atlassian_tool.py` if needed
- Check your Jira instance's custom field configuration

## License

MIT

## Support

For issues or questions:
- Check CrewAI documentation: https://docs.crewai.com
- Atlassian API docs: https://developer.atlassian.com/cloud/jira/platform/rest/v3/

