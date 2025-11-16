from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai.llm import LLM
from typing import List, Optional
import os

from jira_loading_monitor.tools.atlassian_tool import get_active_sprint_board, get_team_member_sprint_issues
from jira_loading_monitor.tools.teams_tool import send_teams_report, send_graph_api_message


@CrewBase
class JiraLoadingMonitor():
    """Jira Loading Progress Monitor crew"""

    agents: List[BaseAgent]
    tasks: List[Task]
    _llm: Optional[LLM] = None  # Cache LLM instance

    # Configure LLM provider
    def _get_llm(self) -> LLM:
        """Get LLM based on environment configuration (cached)"""
        if self._llm is not None:
            return self._llm
        
        # Check which provider is configured in .env
        model = os.getenv('MODEL', 'gpt-4o')
        provider = os.getenv('LLM_PROVIDER', 'openai').lower()
        
        if provider == 'ollama':
            ollama_model = os.getenv('OLLAMA_MODEL', 'llama3.2')
            ollama_base_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
            self._llm = LLM(
                model=f"ollama/{ollama_model}",
                base_url=ollama_base_url
            )
        elif provider == 'anthropic':
            self._llm = LLM(
                model=os.getenv('ANTHROPIC_MODEL', 'claude-3-opus-20240229'),
                api_key=os.getenv('ANTHROPIC_API_KEY')
            )
        else:
            # Default to OpenAI
            self._llm = LLM(
                model=model,
                api_key=os.getenv('OPENAI_API_KEY')
            )
        
        return self._llm
    
    @agent
    def jira_loading(self) -> Agent:
        return Agent(
            config=self.agents_config['jira_loading'], # type: ignore[index]
            llm=self._get_llm(),
            tools=[get_active_sprint_board, get_team_member_sprint_issues],
            verbose=True,
            allow_delegation=False
        )

    @agent
    def reporting_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['reporting_analyst'], # type: ignore[index]
            llm=self._get_llm(),
            tools=[send_teams_report, send_graph_api_message],
            verbose=True,
            allow_delegation=False
        )

    @task
    def check_sprint_loading(self) -> Task:
        return Task(
            config=self.tasks_config['check_sprint_loading'], # type: ignore[index]
            agent=self.jira_loading
        )

    @task
    def generate_sprint_reports(self) -> Task:
        return Task(
            config=self.tasks_config['generate_sprint_reports'], # type: ignore[index]
            agent=self.reporting_analyst,
            context=[self.check_sprint_loading],
            output_file='sprint_loading_report.md'
        )

    @task
    def send_teams_report_task(self) -> Task:
        return Task(
            config=self.tasks_config['send_teams_report'], # type: ignore[index]
            agent=self.reporting_analyst,
            context=[self.generate_sprint_reports]
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Jira Loading Monitor crew"""
        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
        )

