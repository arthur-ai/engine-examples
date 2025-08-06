import os
from typing import Dict, List, Any
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import SystemMessage, HumanMessage
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field

from .tools.github_pr_tool import GitHubPRTool
from .tools.gitlab_pr_tool import GitLabPRTool


class ReleaseNotesRequirements(BaseModel):
    """Release Notes requirements model"""
    features: List[str] = Field(..., description="List of new and large features to be included in the release notes")
    enhancements: List[str] = Field(..., description="List of enhancements to existing features to be included in the release notes")
    bug_fixes: List[str] = Field(..., description="List of bug fixes to existing features to be included in the release notes")
    maintenance: List[str] = Field(..., description="List of maintenance tasks, including dependency updates, changes to CICD, etc. to be included in the release notes")


class ReleaseNotesAgent:
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0.1,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # Initialize tools
        self.github_tool = GitHubPRTool()
        self.gitlab_tool = GitLabPRTool()
        self.tools = [self.github_tool, self.gitlab_tool]
        
        # Create agent
        self.agent_executor = self._create_agent()
        
    def _create_agent(self):
        """Create the LangChain agent with tools"""
        
        system_prompt = """You are an expert technical writer who specializes in creating comprehensive release notes.

Your task is to:
1. Use the available tools to fetch pull requests and merge requests from the provided repositories since the given start date
2. Analyze all the PRs/MRs and categorize them into:
   - New Features: Large new functionality or capabilities
   - Enhancements: Improvements to existing features
   - Bug Fixes: Fixes to issues that users should be aware of
   - Maintenance: Dependency updates, CI/CD changes, internal refactoring, etc.

3. Group related PRs/MRs together (even across repositories) into cohesive release notes
4. Write clear, concise descriptions that are understandable to both customers and developers
5. Include links to the relevant PRs/MRs in each section

You have access to tools for fetching GitHub PRs and GitLab MRs. Use them to gather all the necessary information before drafting the release notes."""

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        agent = create_openai_functions_agent(self.llm, self.tools, prompt)
        return AgentExecutor(agent=agent, tools=self.tools, verbose=True)
    
    def _draft_release_notes(self, repositories: List[str], start_date: str) -> Dict[str, Any]:
        """Draft initial release notes by fetching and analyzing PRs"""
        
        input_text = f"""
        Pull the PRs from the following repositories starting after {start_date}:
        {repositories}

        Analyze the PRs and draft release notes that contain relevant information for:
        - New Features
        - Enhancements to existing features  
        - Bug Fixes
        - Maintenance tasks (dependency updates, changes to CICD, etc.)

        The release notes should be written in a way that is easy to understand and use for
        a customer and developer contributor audience.

        Some PRs may be related (either in the same repo or across repos) and should be grouped
        together into a single release note.
        
        Return the results in JSON format with the following structure:
        {{
            "features": ["list of new features with PR links"],
            "enhancements": ["list of enhancements with PR links"], 
            "bug_fixes": ["list of bug fixes with PR links"],
            "maintenance": ["list of maintenance tasks with PR links"]
        }}
        """
        
        result = self.agent_executor.invoke({"input": input_text})
        return result["output"]
    
    def _review_and_edit(self, draft_notes: str) -> str:
        """Review and edit the draft release notes for clarity and polish"""
        
        review_prompt = f"""
        Review the following draft release notes for clarity, engagement, grammatical accuracy and alignment 
        for a customer and developer contributor audience. Edit and refine the content, ensuring 
        each item is clear, concise, relevant, and grammatically correct.

        Draft Release Notes:
        {draft_notes}

        Provide a polished, error-free release notes document that is clear, engaging and perfectly captures
        all of the relevant work in a consistently categorized and structured way. Format in markdown with a few emojis.
        """
        
        review_result = self.llm.invoke([HumanMessage(content=review_prompt)])
        return review_result.content
    
    def run(self, inputs: Dict[str, Any]) -> str:
        """Run the complete release notes generation process"""
        
        repositories = inputs["repositories"]
        start_date = inputs["start_date"]
        
        print("🔍 Drafting release notes...")
        draft_notes = self._draft_release_notes(repositories, start_date)
        
        print("✏️ Reviewing and editing release notes...")
        final_notes = self._review_and_edit(draft_notes)
        
        return final_notes