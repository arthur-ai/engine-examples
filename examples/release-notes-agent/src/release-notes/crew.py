from crewai import Agent, Crew, Task, Process
from crewai.project import CrewBase, agent, task, crew
from pydantic import BaseModel, Field
from typing import List
from .tools.github_pr_tool import GitHubPRTool
from .tools.gitlab_pr_tool import GitLabPRTool

github_tool = GitHubPRTool()
gitlab_tool = GitLabPRTool()

class ReleaseNotesRequirements(BaseModel):
    """Release Notes requirements model"""
    features: List[str] = Field(..., description="List of new and large features to be included in the release notes")
    enhancements: List[str] = Field(..., description="List of enhancements to existing features to be included in the release notes")
    bug_fixes: List[str] = Field(..., description="List of bug fixes to existing features to be included in the release notes")
    maintenance: List[str] = Field(..., description="List of maintenance tasks, including dependency updates, changes to CICD, etc. to be included in the release notes")

@CrewBase
class ReleaseNotesCrew:
    """Release Notes Crew"""
    agents_config = 'config/agents.yml'
    tasks_config = 'config/tasks.yml'

    @agent
    def writer_agent(self) -> Agent:
        return Agent(
            config = self.agents_config['writer_agent'],
            tools = [gitlab_tool, github_tool],
            verbose = True
        )

    @agent
    def reviewer_agent(self) -> Agent:
        return Agent(
            config = self.agents_config['reviewer_agent'],
            verbose = True,
        )

    @task
    def draft_release_notes(self) -> Task:
        return Task(
            config = self.tasks_config['draft_release_notes_task'],
            agent=self.writer_agent(),
            output_json=ReleaseNotesRequirements,
        )

    @task
    def review_and_edit_release_notes(self) -> Task:
        return Task(
            config = self.tasks_config['review_and_edit_release_notes_task'],
            agent=self.reviewer_agent(),
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents = self.agents,
            tasks = self.tasks,
            process=Process.sequential,
            verbose = True,
        )