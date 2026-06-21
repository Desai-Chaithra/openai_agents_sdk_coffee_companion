## orchestrator.py

import asyncio
import os
import json
from typing import List, Dict, Any, Tuple
from openai import OpenAI, AsyncOpenAI
from dotenv import load_dotenv

from schemas import DrinkSchema, ActivitySchema
from agents import HandOff, barista_agent, companion_agent


# loading the environment variables
# also initializations
load_dotenv(override=True)
api_key = os.environ.get("OPENAI_API_KEY")
aclient = AsyncOpenAI(api_key=api_key)

## maintaing a trace log 
trace_log: List[str] = []


async def simulated_model_lookup_tool(mood: str) -> str:
    await asyncio.sleep(0.1)
    return f"Context Discovery: Inputs indicate the user is currently feeling '{mood}'"

class Runner:
    def __init__(self):
        """Map tool names to actual agent objects"""
        self.agent.registry = {
            "handoff_to_companion_agent": companion_agent,
            "Barista Agent": barista_agent
        }
        self.active_agent = barista_agent
        self.shared_context: Dict[str, Any] = {}

    async def execute_workflow(self, user_mood: str) -> Tuple[str, str, str]:
        trace_log.clear()
        trace_log.append(f"Runner Initialized. Active Entry Node: [{self.active_agent.name}]")

        search_context = await simulated_model_lookup_tool(user_mood)
        self.shared_context["search_context"] = search_context

        drink_output = ""
        activity_output = ""

        while True:
            try:
                trace_log.append(f"Processing inside: [{self.active_agent.name}]")

                handoff_tools = []
                if self.active_agent.name == "Barista Agent":
                    ## CALL AS_TOOL() directly with custom name and description overrides
                    tool = companion_agent.as_tool(
                        name="handoff_to_completion_agent",
                        description="Switch processing tracks over to the Companion Agent for contextual activity pairings."
                    )
                    handoff_tools.append(tool)
                
                messages = [
                    {"role":"system","content":self.active_agent.instructions},
                    {"role":"system","content":self.shared_context.get("latest_prompt", search_context)}
                ]

                completion = await aclient.beta.chat.completions.parse(
                    model="gpt-4o-mini",
                    messages=messages,
                    tools=handoff_tools if handoff_tools else None,
                    response_format=self.active_agent.response_format
                )
                message=completion.choices[0].message

                ## intercept dynamic tool call definitions matched against registry string keys
                if message.tool_calls:
                    tool_call = message.tool_calls[0]
                    function_name = tool_call.function.name
                    arguments = json.loads(tool_call.function.arguments)

                    trace_log.append(f"Model called tool directly:  `{function_name}()`[Reason: {arguments.get('reason')}]")

                    if message.parsed:
                        drink_data: DrinkSchema = message.parsed 

                        ## output safety guardrails
                        if "stress" in user_mood.lower() or "anxious" in user_mood.lower():
                            if drink_data.caffeine_level.lower() == "high":
                                trace_log.append("Guardrail Intercept: Overriding high caffeine with warm chamomile Tea.")
                                drink_data.drink_name = "Warm Chamomile Tea with Honey"
                                drink_data.caffeine_level = "None"
                        
                        self.shared_context["drink_data"] = drink_data
                        drink_output = f"Drink: {drink_data.drink_name}\n Caffeine Level: {drink_data.caffeine_level}"
                    
                    raise HandOff(target_agent_name = function_name, dynamic_context = self.shared_context)
                
                else:
                    if self.active_agent.name == "Companion Agent" and message.parsed:
                        activity_data: ActivitySchema = message.parsed
                        activity_output = f"Activity: {activity_data.paired_activity}\n\n Reflection: {activity_data.rationale}"
                
            except HandOff as handoff_event:
                trace_log.append(f" Context intercepted. Switching runtime state to tool target function mapping.")
                self.active_agent = self.agent_registry[handoff_event.target_agent_name]
                
                passed_drink = handoff_event.dynamic_context["drink_data"]
                self.shared_context["latest_prompt"] = f"The user feels '{user_mood}' and was served '{passed_drink.drink_name}'."
                continue

            return drink_output, activity_output, "\n".join(trace_log)

