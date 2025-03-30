from typing import List, cast

import chainlit as cl
from autogen_agentchat.base import TaskResult
from autogen_agentchat.conditions import TextMentionTermination, MaxMessageTermination, TimeoutTermination
from autogen_agentchat.messages import ModelClientStreamingChunkEvent, TextMessage
from autogen_agentchat.teams import RoundRobinGroupChat, SelectorGroupChat
from autogen_core import CancellationToken
from agents import get_participants
from model_provider import create_model_client

@cl.on_chat_start  # type: ignore
async def start_chat() -> None:

    # Termination condition.
    text_mention_termination = TextMentionTermination("TERMINATE")
    max_messages_termination = MaxMessageTermination(max_messages=25)
    timeout_termination = TimeoutTermination(timeout_seconds=60 * 5)  # 5 minutes timeout
    termination = text_mention_termination | max_messages_termination | timeout_termination

    # Chain the assistant, critic and user agents using RoundRobinGroupChat.
    group_chat = RoundRobinGroupChat(        
        participants=get_participants(),
        max_turns=5,    
        termination_condition=termination)
    
    selector_group_chat = SelectorGroupChat(
        participants=get_participants(),
        model_client=create_model_client("gpt-4o-mini"),
        termination_condition=termination,
        allow_repeated_speaker=True,
        max_selector_attempts=3,
        selector_prompt=
        """
        You are in a role play game. The final goal is to create a high-level architecture 
        using the best practices from the Azure Architecture Center and the Cloud Adoption Framework.
        Initially the user provides a message with the architecture requirements.
        Then the questioner agent asks questions to gather information about the user's Azure architecture project.
        The user input agent provides the user input to the questioner agent.
        The architect agent creates a high-level architecture using the information provided by the user.
        The illustrator agent creates a flowchart diagram using the Mermaid syntax based on the high-level architecture provided by the architect agent.
        The user approval agent approves or rejects the architecture.
        Each agent has its own role and should not interfere with the other agents.
        Each agent should be selected to perform its own task.
        Use the appropriate role to perform the task.
        If the solution is approved by the user, the task is complete.
        If the solution is rejected by the user, start by questioning the user again.
        
        Select an agent to perform task.

        {roles}

        Current conversation context:
        {history}

        Read the above conversation, then select an agent from {participants} to perform the next task.
        When the task is complete, let the user approve or disapprove the task.
        """
    )

    # Set the assistant agent in the user session.
    cl.user_session.set("prompt_history", "")  # type: ignore
    cl.user_session.set("team", group_chat)  # type: ignore
    #cl.user_session.set("team", selector_group_chat)  # type: ignore


@cl.set_starters  # type: ignore
async def set_starts() -> List[cl.Starter]:
    return [
        cl.Starter(
            label="Azure App Modernization",
            message="Explain the benefits of modernizing applications using Azure services.",
        ),
        cl.Starter(
            label="Azure AI Benefits",
            message="Describe how Azure AI can be used to enhance business processes.",
        ),
        cl.Starter(
            label="Azure DevOps",
            message="Outline the steps to set up a CI/CD pipeline using Azure DevOps.",
        ),
    ]


@cl.on_message  # type: ignore
async def chat(message: cl.Message) -> None:
    # Get the team from the user session.
    team = cast(RoundRobinGroupChat,
                cl.user_session.get("team"))  # type: ignore
    # Streaming response message.
    streaming_response: cl.Message | None = None
    # Stream the messages from the team.
    async for msg in team.run_stream(
        task=[TextMessage(content=message.content, source="user")],
        cancellation_token=CancellationToken(),
    ):
        # Print the name of the agent that is sending the message
        if hasattr(msg, 'source') and msg.source:
            print(f"Agent in use: {msg.source}")
        
        if isinstance(msg, ModelClientStreamingChunkEvent):
            print(f"Agent starting response: {msg.source}")
            # Stream the model client response to the user.
            if streaming_response is None:
                # Start a new streaming response.
                streaming_response = cl.Message(content="", author=msg.source)
                # Print when a new agent starts responding                
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
