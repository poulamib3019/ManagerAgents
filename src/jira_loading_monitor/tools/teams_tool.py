"""Microsoft Teams integration tools for CrewAI"""

from crewai_tools import tool
import os
from typing import Optional
import requests
import json


@tool("Send Report via Teams Chat")
def send_teams_report(report_content: str, recipient_email: str = "bala.poulami@outlook.com") -> str:
    """
    Send a report via Microsoft Teams chat to a specified email address.
    
    Args:
        report_content: The content of the report to send
        recipient_email: The email address of the recipient (default: bala.poulami@outlook.com)
    
    Returns:
        Status message indicating success or failure
    """
    teams_webhook_url = os.getenv('TEAMS_WEBHOOK_URL')
    
    if not teams_webhook_url:
        # Alternative: Use Microsoft Graph API if webhook not available
        return f"Teams webhook not configured. Report content:\n\n{report_content}\n\nTo configure Teams integration, set TEAMS_WEBHOOK_URL in .env or use Microsoft Graph API."
    
    try:
        # Format message for Teams
        message = {
            "@type": "MessageCard",
            "@context": "https://schema.org/extensions",
            "summary": "Sprint Loading Report",
            "themeColor": "0078D4",
            "title": "Jira Sprint Loading Progress Report",
            "sections": [
                {
                    "activityTitle": f"Report sent to: {recipient_email}",
                    "text": report_content,
                    "markdown": True
                }
            ]
        }
        
        response = requests.post(
            teams_webhook_url,
            json=message,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            return f"✓ Report successfully sent to {recipient_email} via Microsoft Teams"
        else:
            return f"Error sending report: {response.status_code} - {response.text}"
            
    except Exception as e:
        return f"Error sending Teams message: {str(e)}\n\nReport content:\n{report_content}"


@tool("Send Message via Microsoft Graph API")
def send_graph_api_message(report_content: str, recipient_email: str = "bala.poulami@outlook.com") -> str:
    """
    Send a report via Microsoft Graph API (requires OAuth setup).
    This is an alternative method if webhook is not available.
    
    Args:
        report_content: The content of the report to send
        recipient_email: The email address of the recipient
    
    Returns:
        Status message
    """
    graph_api_token = os.getenv('MICROSOFT_GRAPH_API_TOKEN')
    sender_email = os.getenv('MICROSOFT_GRAPH_SENDER_EMAIL')
    
    if not all([graph_api_token, sender_email]):
        return "Microsoft Graph API not configured. Set MICROSOFT_GRAPH_API_TOKEN and MICROSOFT_GRAPH_SENDER_EMAIL in .env"
    
    try:
        # Send message via Graph API
        url = f"https://graph.microsoft.com/v1.0/users/{sender_email}/sendMail"
        
        message = {
            "message": {
                "subject": "Jira Sprint Loading Progress Report",
                "body": {
                    "contentType": "Text",
                    "content": report_content
                },
                "toRecipients": [
                    {
                        "emailAddress": {
                            "address": recipient_email
                        }
                    }
                ]
            }
        }
        
        headers = {
            "Authorization": f"Bearer {graph_api_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(url, json=message, headers=headers)
        
        if response.status_code in [200, 202]:
            return f"✓ Report successfully sent to {recipient_email} via Microsoft Graph API"
        else:
            return f"Error sending via Graph API: {response.status_code} - {response.text}"
            
    except Exception as e:
        return f"Error with Graph API: {str(e)}"

