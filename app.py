import os
from typing import List, cast
import asyncio
import chainlit as cl
from autogen_agentchat.base import TaskResult
from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.messages import ModelClientStreamingChunkEvent, TextMessage
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_core import CancellationToken
from agents import get_agents
from models import get_model_client   

@cl.on_chat_start
async def start_chat():
    # Get model client
    model_client = get_model_client("phi4_mini")

    # Get agents 
    agents = get_agents(model_client)

    # Create a group chat with the agents
     # Termination condition.
    termination = TextMentionTermination("APPROVE", sources=["critic"])
    group_chat = RoundRobinGroupChat(agents, termination_condition=termination)

    # Set the assistant agent in the user session.
    cl.user_session.set("prompt_history", "")
    cl.user_session.set("team", group_chat)


@cl.set_starters
async def set_starts() -> List[cl.Starter]:
    return [
        cl.Starter(
            label="Azure App Modernization",
            message="Explain the benefits of modernizing applications using Azure services.",
        ),
        cl.Starter(
            label="Azure AI",
            message="Describe how Azure AI can be used to enhance business processes.",
        ),
        cl.Starter(
            label="Azure DevOps",
            message="Outline the steps to set up a CI/CD pipeline using Azure DevOps.",
        ),
    ]


@cl.on_message
async def chat(message: cl.Message) -> None:
    # Get the team from the user session.
    team = cast(RoundRobinGroupChat, cl.user_session.get("team"))

    # Streaming response message.
    streaming_response: cl.Message | None = None
    
    # Stream the messages from the team.
    async for msg in team.run_stream(
        task=[TextMessage(content=message.content, source="user")],
        cancellation_token=CancellationToken(),
    ):
        if isinstance(msg, ModelClientStreamingChunkEvent):
            # Stream the model client response to the user.
            if streaming_response is None:
                # Start a new streaming response.
                streaming_response = cl.Message(content=msg.source + ": ", author=msg.source)
            await streaming_response.stream_token(msg.content)
        elif streaming_response is not None:
            # Done streaming the model client response.
            # We can skip the current message as it is just the complete message
            # of the streaming response.
            await streaming_response.send()
            # Reset the streaming response so we won't enter this block again
            # until the next streaming response is complete.
            streaming_response = None
        elif isinstance(msg, TaskResult):
            # Send the task termination message.
            final_message = "Task terminated. "
            if msg.stop_reason:
                final_message += msg.stop_reason
            await cl.Message(content=final_message).send()
        else:
            # Skip all other message types.
            pass
