from typing import List, cast

import chainlit as cl
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.base import Response
from autogen_agentchat.messages import ModelClientStreamingChunkEvent, TextMessage
from autogen_core import CancellationToken
from model_provider import create_model_client
from tools import get_date, generate_mermaid_diagram



@cl.set_starters  # type: ignore
async def set_starts() -> List[cl.Starter]:
    return [
        cl.Starter(
            label="Date",
            message="What date is it today?",
        ),
        cl.Starter(
            label="Mermaid Diagram",
            message="""
            flowchart TD
                A[User Interface] -->|User Input| B[Azure Functions]
                B -->|Invoke Search| C[Azure Cognitive Search]
                C -->|Retrieve Relevant Docs| D[Azure Blob Storage]
                B -->|Process and Generate| E[Azure OpenAI Service]
                E -->|Return Response| B
                B -->|Send Output| A
                B -->|Log Data| F[Azure Application Insights]
            """,
        ),
    ]


@cl.step(type="tool")  # type: ignore
async def get_weather(city: str) -> str:
    """Get the weather for a given city."""
    return f"The weather in {city} is 73 degrees and Sunny."


@cl.on_chat_start  # type: ignore
async def start_chat() -> None:    

    # Create the assistant agent with the get_weather tool.
    assistant = AssistantAgent(
        name="assistant",
        tools=[generate_mermaid_diagram],
        model_client=create_model_client(
            "mistral-small-2503", 
            function_calling=True,
            json_output=True), # Enable JSON output for function calling.),
        system_message="You are a helpful assistant",
        model_client_stream=True,  # Enable model client streaming.
        reflect_on_tool_use=True,  # Reflect on tool use.
    )

    # Set the assistant agent in the user session.
    cl.user_session.set("prompt_history", "")  # type: ignore
    cl.user_session.set("agent", assistant)  # type: ignore


@cl.on_message  # type: ignore
async def chat(message: cl.Message) -> None:
    # Get the assistant agent from the user session.
    agent = cast(AssistantAgent, cl.user_session.get("agent"))  # type: ignore
    # Construct the response message.
    response = cl.Message(content="")
    async for msg in agent.on_messages_stream(
        messages=[TextMessage(content=message.content, source="user")],
        cancellation_token=CancellationToken(),
    ):
        if isinstance(msg, ModelClientStreamingChunkEvent):
            # Stream the model client response to the user.
            await response.stream_token(msg.content)
        elif isinstance(msg, Response):
            # Done streaming the model client response. Send the message.
            await response.send()