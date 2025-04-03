from typing import List, cast, Optional, Dict
import re
import os
from dotenv import load_dotenv
import chainlit as cl
from autogen_agentchat.base import TaskResult
from autogen_agentchat.conditions import TextMentionTermination, MaxMessageTermination, TimeoutTermination
from autogen_agentchat.messages import ModelClientStreamingChunkEvent, TextMessage
from autogen_agentchat.teams import RoundRobinGroupChat, SelectorGroupChat
from autogen_core import CancellationToken
from agents import get_participants
from model_provider import create_model_client

# Load environment variables from .env file
load_dotenv(override=True)


# @cl.oauth_callback
# async def oauth_callback(
#     provider_id: str,
#     token: str,
#     raw_user_data: Dict[str, str],
#     default_user: cl.User,
# ) -> Optional[cl.User]:
#     print(
#         f"OAuth callback for provider {provider_id} with token {token} and user data {raw_user_data}")
#     return default_user


@cl.on_chat_start  # type: ignore
async def start_chat() -> None:
    load_dotenv(override=True)
    # Termination condition.
    text_mention_termination = TextMentionTermination("TERMINATE")
    max_messages_termination = MaxMessageTermination(max_messages=25)
    timeout_termination = TimeoutTermination(
        timeout_seconds=60 * 5)  # 5 minutes timeout
    termination = text_mention_termination | max_messages_termination | timeout_termination

    # Chain the assistant, critic and user agents using RoundRobinGroupChat.
    group_chat = RoundRobinGroupChat(
        participants=get_participants(),
        max_turns=3,
        termination_condition=termination)

    selector_group_chat = SelectorGroupChat(
        participants=get_participants(),
        model_client=create_model_client("gpt-4o-mini"),
        termination_condition=termination,
        allow_repeated_speaker=True,
        max_selector_attempts=3,
        selector_prompt="""
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
    # cl.user_session.set("team", selector_group_chat)  # type: ignore


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
        cl.Starter(
            label="AI Agent",
            message="Build an AI agent with a FE, BE, and a database.",
        ),
    ]


@cl.on_message  # type: ignore
async def chat(message: cl.Message) -> None:
    # Get the assistant agent from the user session.
    agent = cast(RoundRobinGroupChat,
                 cl.user_session.get("team"))  # type: ignore
    # Construct the response message.
    response = cl.Message(content="")
    current_source = None

    async for msg in agent.run_stream(
        task=[TextMessage(content=message.content, source="user")],
        cancellation_token=CancellationToken(),
    ):
        if isinstance(msg, ModelClientStreamingChunkEvent):
            # If source has changed, update the message with a header showing the source
            if current_source != msg.source:
                current_source = msg.source
                if response.content:
                    # Send the current response before starting a new one from different source
                    await response.send()
                    # Process the response content for images
                    await process_response_content(response)
                    # Create a new response message with source header
                    response = cl.Message(
                        content=f"**[{current_source}]**\n\n")
                else:
                    # First response, just add the source header
                    response.content = f"**[{current_source}]**\n\n"

            # Stream the model client response to the user.
            await response.stream_token(msg.content)
        elif isinstance(msg, TaskResult):
            # Done streaming the model client response. Send the message.
            await response.send()

            # Process the response content for images
            await process_response_content(response)


async def process_response_content(response: cl.Message) -> None:
    """Process the response content to handle image filenames and Markdown image tags."""
    # Check if response contains an image filename
    content = response.content
    if content and isinstance(content, str):
        # Check for Markdown image tags and remove them
        markdown_img_pattern = r'!\[Diagram]\(.*?\)'
        if re.search(markdown_img_pattern, content):
            # Remove Markdown image tags
            cleaned_content = re.sub(markdown_img_pattern, '', content)
            # Update the message content
            await response.update(content=cleaned_content)
            # Refresh content variable with cleaned content
            content = cleaned_content

        # Look for image filenames (UUID format with png/jpg/etc extension)
        image_pattern = r'([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\.(png|jpg|jpeg|svg|pdf|gif))'
        matches = re.findall(image_pattern, content)

        if matches:
            for match in matches:
                filename = match[0]  # Get the full filename

                # Build the path to the image
                src_dir = os.path.dirname(os.path.abspath(__file__))
                image_path = os.path.join(src_dir, '.files', filename)

                # Check if the file exists
                if os.path.exists(image_path):
                    # Display the image
                    image_element = cl.Image(
                        path=image_path,
                        name=filename,
                        display="inline"
                    )
                    await image_element.send(for_id=response.id)
