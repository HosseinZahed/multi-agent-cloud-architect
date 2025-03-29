import os
from typing import List, cast
import asyncio
import chainlit as cl

@cl.on_chat_start
async def start_chat():
    # Set up the model

    # Set up the agents

    # Set the assistant agent in the user session.
    cl.user_session.set("prompt_history", "")
    #cl.user_session.set("team", group_chat)


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
    return None