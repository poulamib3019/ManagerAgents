"""Atlassian Jira integration tools for CrewAI"""

from crewai_tools import tool
from typing import Optional
import os
from atlassian import Jira


@tool("Get Active Sprint Board")
def get_active_sprint_board(project_key: str, board_id: Optional[int] = None) -> str:
    """
    Retrieve the active sprint board for a Jira project.
    
    Args:
        project_key: The Jira project key (e.g., 'PROJ')
        board_id: Optional board ID, if None will find first available board
    
    Returns:
        JSON string containing sprint board data including issues, team members, and story points
    """
    jira_url = os.getenv('JIRA_URL')
    jira_username = os.getenv('JIRA_USERNAME')
    jira_api_token = os.getenv('JIRA_API_TOKEN')
    
    if not all([jira_url, jira_username, jira_api_token]):
        return "Error: Jira credentials not configured. Please set JIRA_URL, JIRA_USERNAME, and JIRA_API_TOKEN in .env"
    
    try:
        jira = Jira(
            url=jira_url,
            username=jira_username,
            password=jira_api_token
        )
        
        # Get active sprints
        if board_id:
            sprints = jira.get_all_sprints(board_id, state='active')
        else:
            # Try to find board for project
            boards = jira.get_all_boards(projectKey=project_key)
            if not boards['values']:
                return f"Error: No boards found for project {project_key}"
            board_id = boards['values'][0]['id']
            sprints = jira.get_all_sprints(board_id, state='active')
        
        if not sprints:
            return f"Error: No active sprints found for project {project_key}"
        
        active_sprint = sprints[0]
        sprint_id = active_sprint['id']
        
        # Get issues in sprint
        issues = jira.get_sprint_issues(sprint_id)
        
        # Analyze story points per assignee
        story_points_by_member = {}
        for issue in issues['issues']:
            assignee = issue['fields'].get('assignee', {}).get('displayName', 'Unassigned')
            story_points = issue['fields'].get('customfield_10016', 0) or 0  # Story points field
            
            if assignee not in story_points_by_member:
                story_points_by_member[assignee] = {
                    'total_points': 0,
                    'issues': []
                }
            
            story_points_by_member[assignee]['total_points'] += story_points
            story_points_by_member[assignee]['issues'].append({
                'key': issue['key'],
                'summary': issue['fields']['summary'],
                'points': story_points
            })
        
        result = {
            'sprint': active_sprint['name'],
            'sprint_id': sprint_id,
            'team_members': story_points_by_member
        }
        
        import json
        return json.dumps(result, indent=2)
        
    except Exception as e:
        return f"Error retrieving sprint board: {str(e)}"


@tool("Get Sprint Issues for Team Member")
def get_team_member_sprint_issues(project_key: str, assignee: str, sprint_id: Optional[int] = None) -> str:
    """
    Get all issues assigned to a specific team member in the active sprint.
    
    Args:
        project_key: The Jira project key
        assignee: The team member's email or username
        sprint_id: Optional sprint ID, if None uses active sprint
    
    Returns:
        JSON string with issues and story points for the team member
    """
    jira_url = os.getenv('JIRA_URL')
    jira_username = os.getenv('JIRA_USERNAME')
    jira_api_token = os.getenv('JIRA_API_TOKEN')
    
    if not all([jira_url, jira_username, jira_api_token]):
        return "Error: Jira credentials not configured"
    
    try:
        jira = Jira(
            url=jira_url,
            username=jira_username,
            password=jira_api_token
        )
        
        # Build JQL query
        jql = f'project = {project_key} AND assignee = "{assignee}" AND sprint in openSprints()'
        
        issues = jira.jql(jql)
        
        total_points = 0
        issue_list = []
        
        for issue in issues['issues']:
            points = issue['fields'].get('customfield_10016', 0) or 0
            total_points += points
            issue_list.append({
                'key': issue['key'],
                'summary': issue['fields']['summary'],
                'status': issue['fields']['status']['name'],
                'story_points': points
            })
        
        result = {
            'assignee': assignee,
            'total_story_points': total_points,
            'issue_count': len(issue_list),
            'issues': issue_list
        }
        
        import json
        return json.dumps(result, indent=2)
        
    except Exception as e:
        return f"Error retrieving team member issues: {str(e)}"


