try:
    from crewai import Agent, Task, Crew, Process
    CREWAI_AVAILABLE = True
except ImportError:
    Agent = Task = Crew = Process = None
    CREWAI_AVAILABLE = False

import ollama
from typing import List

class JarvisAgents:
    def __init__(self):
        self.llm = "ollama/llama3"  # or groq etc.

    def researcher(self):
        if not CREWAI_AVAILABLE:
            return None
        return Agent(
            role='Researcher',
            goal='Gather accurate information and tools for tasks',
            backstory='Expert researcher with access to web tools',
            verbose=True,
            llm=self.llm,
            tools=[]  # Add Serper etc. later
        )

    def critic(self):
        if not CREWAI_AVAILABLE:
            return None
        return Agent(
            role='Critic',
            goal='Evaluate and optimize responses for self-improvement',
            backstory='Self-aware optimizer',
            verbose=True,
            llm=self.llm
        )

    def planner(self):
        if not CREWAI_AVAILABLE:
            return None
        return Agent(
            role='Planner',
            goal='Break down complex commands into steps',
            backstory='Strategic planner',
            verbose=True,
            llm=self.llm
        )

    def create_crew(self, task_description):
        if not CREWAI_AVAILABLE:
            class SimpleCrew:
                def __init__(self, description):
                    self.description = description

                def kickoff(self):
                    return f"Fallback agent result for: {self.description}"

            return SimpleCrew(task_description)

        researcher = self.researcher()
        critic = self.critic()
        planner = self.planner()

        task1 = Task(description=f"Plan: {task_description}", agent=planner, expected_output="Step-by-step plan")
        task2 = Task(description=f"Research and execute: {task_description}", agent=researcher, expected_output="Detailed response")
        task3 = Task(description="Critique and optimize the response", agent=critic, expected_output="Improved final output")

        crew = Crew(
            agents=[planner, researcher, critic],
            tasks=[task1, task2, task3],
            process=Process.sequential,
            verbose=True
        )
        return crew
