"""
This file handles the structured blueprints. It contains your custom HandOff exception
engine, the core Agent framework class, instantiates the specific agent
configurations
"""

## agents.py
from typing import Any, Dict
from schemas import DrinkSchema, ActivitySchema

class HandOff(Exception):
    """Signals a structural shift of execution context from one Agent node to another."""
    def __init__(self, target_agent_name: str, dynamic_context: Dict[str, Any]):
        self.target_agent_name = target_agent_name
        self.dynamic_context = dynamic_context

class Agent:
    def __init__(self, name: str, instructions: str, response_format: Any):
        self.name = name
        self.instructions = instructions
        self.response_format = response_format
    
    def as_tool(self, name: str = None, description: str = None) -> Dict[str, Any]:
        """
        converts the Agent configuraiton directly into an OpenAI function tool block,
        allowing direct overrides for custom tool names and descriptions.
        """
        final_name = name if name else f"handoff_to_{self.name.lower().replace(' ','-')}"
        final_description = description if description else f"Call this function to a handoff execution control to the specialized {self.name}"

        return {
            "typw":"function",
            "function":{
                "name":final_name,
                "description":{
                    "type":"object",
                    "properties":{
                        "reason":{
                            "type":"string",
                            "description":"The justification explaining why this action or handoff is occuring."
                        }
                    },
                    "required":["reason"]
                }
            }
        }

## instantiate baseline blueprints
barista_agent = Agent(
    name = "Barista Agent",
    instructions="Select the perfect warm beverage (coffee, tea, or hearbal drink) based on the user's mood description.",
    response_format=DrinkSchema
)

companion_agent = Agent(
    name="Companion Agent",
    instructions="Provide a small, comforting 2-minute activity that pairs nicely with the chosen drink and the user's emotional state.",
    response_format=ActivitySchema
)