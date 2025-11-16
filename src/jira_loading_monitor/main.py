#!/usr/bin/env python
import sys
import os
import warnings
from datetime import datetime
from dotenv import load_dotenv

from jira_loading_monitor.crew import JiraLoadingMonitor

# Load environment variables
load_dotenv()

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")


def run():
    """
    Run the Jira Loading Monitor crew.
    """
    inputs = {
        'project_key': os.getenv('JIRA_PROJECT_KEY', 'PROJ'),  # Change to your project key
        'current_sprint': f"Active Sprint - {datetime.now().strftime('%Y-%m-%d')}"
    }

    try:
        result = JiraLoadingMonitor().crew().kickoff(inputs=inputs)
        print("\n" + "="*50)
        print("Jira Loading Monitor Execution Complete")
        print("="*50)
        return result
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")


if __name__ == "__main__":
    run()

