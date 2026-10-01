from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from pydantic import BaseModel, Field
from .tools.push_tool import send_push_notification
from crewai_tools import SerperDevTool


# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

class TrendingCompany(BaseModel):
    """ A company is in news, attracting attention
      and trending in the stock market."""
    name: str = Field(..., description="The name of the trending company")
    ticker: str = Field(..., description="The stock ticker symbol of the trending company")
    reason: str = Field(..., description="The reason why the company is trending")
    popularity: str = Field(..., description="The popularity or public attention the trending company is receiving")
    sentiment: str = Field(..., description="The overall market sentiment towards the trending company")
    expert_opinion: str = Field(..., description="The expert opinion or analysis on the trending company")
    historical_performance: str = Field(..., description="The historical performance of the trending company's stock")

class TrendingCompanyList(BaseModel):
    """A list of trending companies that are in news."""
    companies: list[TrendingCompany] = Field(..., description="A list of trending companies in the news")
    total_companies: int = Field(..., description="The total number of trending companies in the news")



class  TrendingCompanyResearch(BaseModel):
    """Details of the research conducted on a trending company."""
    name: str = Field(..., description="The name of the trending company being researched")
    market_position: str = Field(..., description="The current market position of the trending company and competitive analysis")
    future_outlook: str = Field(..., description="The future outlook of the trending company and growth prospects")
    investment_potential: str = Field(..., description="The investment potential and suitability of the trending company")
    sentiment: str = Field(..., description="The overall market sentiment towards the trending company")
    expert_opinion: str = Field(..., description="The expert opinion or analysis on the trending company")
    historical_performance: str = Field(..., description="The historical performance of the trending company's stock")
    popularity: str = Field(..., description="The popularity or public attention the trending company is receiving")


class TrendingCompanyResearchList(BaseModel):
    """A list of research reports on all trending companies."""
    research_reports: list[TrendingCompanyResearch] = Field(..., description="Comprehensive research reports on trending companies")

@CrewBase
class StockPicker():
    """StockPicker crew"""

    agents: list[BaseAgent]
    tasks: list[Task]

    # Learn more about YAML configuration files here:
    # Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
    # Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
    
    # If you would like to add tools to your agents, you can learn more about it here:
    # https://docs.crewai.com/concepts/agents#agent-tools
    @agent
    def trending_company_finder(self) -> Agent:
        return Agent(
            config=self.agents_config['trending_company_finder'], # type: ignore[index]
            tools=[SerperDevTool()], memory=True
          
            
        )

    @agent
    def financial_researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['financial_researcher'],
             tools=[SerperDevTool()], memory=True # type: ignore[index]
            
        )
    @agent
    def stock_picker(self) -> Agent:
        return Agent(
            config=self.agents_config['stock_picker'], # type: ignore[index]
            tools=[send_push_notification], memory=True)          
        
    # To learn more about structured task outputs,
    # task dependencies, and task callbacks, check out the documentation:
    # https://docs.crewai.com/concepts/tasks#overview-of-a-task
    @task
    def find_trending_companies(self) -> Task:
        return Task(
            config=self.tasks_config['find_trending_companies'],
            output_pydantic=TrendingCompanyList,
               # type: ignore[index]
        )

    
    @task
    def research_trending_companies(self) -> Task:
        return Task(
            config=self.tasks_config['research_trending_companies'],
            output_pydantic=TrendingCompanyResearchList,  # type: ignore[index]
         
        )
    @task
    def pick_best_company(self) -> Task:
        return Task(
            config=self.tasks_config['pick_best_company'],
                 
        )

    @crew
    def crew(self) -> Crew:
        """Creates the StockPicker crew"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge
        manager=Agent(
            config=self.agents_config['manager'], # type: ignore[index]
            allow_delegation=True,
        )
        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.hierarchical,
            verbose=True,
            memory=True,
            tracing=True,
            manager_agent=manager,

            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )
