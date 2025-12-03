from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
from multi_agent_crew.tools import WeatherTool, GSCTool, KeywordSearchTool

@CrewBase
class WeatherCrew():
    """WeatherCrew - A multi-agent crew for weather and SEO analysis"""

    agents: List[BaseAgent]
    tasks: List[Task]

    @agent
    def weather_reporter(self) -> Agent:
        return Agent(
            config=self.agents_config['weather_reporter'], # type: ignore[index]
            verbose=True,
            tools=[WeatherTool()]
        )

    @agent
    def seo_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['seo_analyst'], # type: ignore[index]
            verbose=True,
            tools=[GSCTool(), KeywordSearchTool()]
        )

    @task
    def report_weather_task(self) -> Task:
        return Task(
            config=self.tasks_config['report_weather_task'], # type: ignore[index]
        )

    @task
    def fetch_gsc_keywords_task(self) -> Task:
        return Task(
            config=self.tasks_config['fetch_gsc_keywords_task'], # type: ignore[index]
        )

    @task
    def verify_keyword_rankings_task(self) -> Task:
        return Task(
            config=self.tasks_config['verify_keyword_rankings_task'], # type: ignore[index]
        )

    @crew
    def crew(self) -> Crew:
        """Creates the multi-agent crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
