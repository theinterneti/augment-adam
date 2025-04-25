#!/usr/bin/env python
"""
Agent Coordination Example for Augment Adam

This script demonstrates how to coordinate multiple agents to work together.
"""

from augment_adam.ai_agent.coordination.coordinator import Coordinator
from augment_adam.ai_agent.coordination.team import Team
from augment_adam.ai_agent.types.research_agent import ResearchAgent
from augment_adam.ai_agent.types.coding_agent import CodingAgent
from augment_adam.ai_agent.types.creative_agent import CreativeAgent
from augment_adam.memory import FAISSMemory

def main():
    """Run the agent coordination example."""
    print("Augment Adam Agent Coordination Example")
    print("=" * 50)
    
    # Create a shared memory for the agents
    print("\n1. Creating shared memory...")
    shared_memory = FAISSMemory()
    print("   ✓ Shared memory created")
    
    # Create specialized agents
    print("\n2. Creating specialized agents...")
    research_agent = ResearchAgent(
        name="Researcher",
        description="Specializes in finding and analyzing information",
        memory=shared_memory
    )
    
    coding_agent = CodingAgent(
        name="Coder",
        description="Specializes in writing and debugging code",
        memory=shared_memory
    )
    
    creative_agent = CreativeAgent(
        name="Creator",
        description="Specializes in generating creative content and ideas",
        memory=shared_memory
    )
    
    print("   ✓ Specialized agents created")
    
    # Create a team of agents
    print("\n3. Creating a team...")
    team = Team(
        name="Project Team",
        agents=[research_agent, coding_agent, creative_agent],
        shared_memory=shared_memory
    )
    print("   ✓ Team created")
    
    # Create a coordinator to manage the team
    print("\n4. Creating a coordinator...")
    coordinator = Coordinator(team=team)
    print("   ✓ Coordinator created")
    
    # Define a complex task that requires multiple agents
    print("\n5. Defining a complex task...")
    task = {
        "title": "Create a weather dashboard",
        "description": "Research weather APIs, write code to fetch data, and design a user interface",
        "steps": [
            {"name": "Research", "description": "Find suitable weather APIs", "assigned_to": "Researcher"},
            {"name": "Implementation", "description": "Write code to fetch and process weather data", "assigned_to": "Coder"},
            {"name": "Design", "description": "Create a user-friendly dashboard design", "assigned_to": "Creator"}
        ]
    }
    print("   ✓ Task defined")
    
    # Execute the task using the coordinator
    print("\n6. Executing the task...")
    print("\n   Coordinator is analyzing the task...")
    
    # Simulate the coordinator assigning tasks to agents
    print("\n   Coordinator is assigning tasks to agents...")
    for step in task["steps"]:
        print(f"   - Assigning '{step['name']}' to {step['assigned_to']}")
    
    # Simulate the research agent's work
    print("\n   Researcher is working on finding weather APIs...")
    research_results = {
        "apis": [
            {"name": "OpenWeatherMap", "url": "https://openweathermap.org/api", "features": ["Current weather", "Forecasts", "Historical data"]},
            {"name": "WeatherAPI", "url": "https://www.weatherapi.com/", "features": ["Real-time weather", "Forecasts", "Astronomy"]}
        ],
        "recommendation": "OpenWeatherMap is recommended for its comprehensive features and reliable service."
    }
    
    # Add research results to shared memory
    shared_memory.add(
        f"Weather API Research Results: {research_results['recommendation']}",
        {"type": "research", "task": "weather_api"}
    )
    print("   ✓ Research completed and results added to shared memory")
    
    # Simulate the coding agent's work
    print("\n   Coder is implementing the weather data fetching code...")
    code_snippet = """
import requests

def get_weather_data(city, api_key):
    \"\"\"Fetch weather data for a city using OpenWeatherMap API.\"\"\"
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    response = requests.get(url)
    return response.json()

def parse_weather_data(data):
    \"\"\"Parse the weather data into a more usable format.\"\"\"
    return {
        "city": data["name"],
        "temperature": data["main"]["temp"],
        "humidity": data["main"]["humidity"],
        "description": data["weather"][0]["description"],
        "icon": data["weather"][0]["icon"]
    }
"""
    
    # Add code to shared memory
    shared_memory.add(
        "Weather data fetching code",
        {"type": "code", "language": "python", "task": "weather_data_fetching"}
    )
    print("   ✓ Code implementation completed and added to shared memory")
    
    # Simulate the creative agent's work
    print("\n   Creator is designing the dashboard UI...")
    design_description = """
Weather Dashboard Design:
- Clean, minimalist interface with a blue and white color scheme
- Large temperature display in the center
- Weather condition icon next to the temperature
- Additional metrics (humidity, wind speed) displayed below
- 5-day forecast at the bottom of the screen
- Search bar at the top for changing locations
- Responsive design that works on both desktop and mobile
"""
    
    # Add design to shared memory
    shared_memory.add(
        "Weather dashboard design",
        {"type": "design", "task": "dashboard_ui"}
    )
    print("   ✓ Design completed and added to shared memory")
    
    # Coordinator combines the results
    print("\n   Coordinator is combining the results...")
    
    # Retrieve all task results from memory
    results = shared_memory.retrieve("weather dashboard", n_results=3)
    result_texts = [item[0]["text"] for item in results]
    
    print("\n   Final combined result:")
    print("   " + "-" * 40)
    print("   Weather Dashboard Project Completed")
    print("   " + "-" * 40)
    for i, text in enumerate(result_texts):
        print(f"   Component {i+1}: {text}")
    
    print("\n" + "=" * 50)
    print("Agent Coordination Example Completed!")
    print("This example demonstrates how multiple specialized agents can work together on a complex task.")

if __name__ == "__main__":
    main()
