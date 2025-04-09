import os
from typing import List, Optional, Dict
import chainlit as cl
import semantic_kernel as sk
from semantic_kernel.agents import AgentGroupChat
from semantic_kernel.agents.strategies import TerminationStrategy
from semantic_kernel.contents import AuthorRole, ChatMessageContent, ChatHistory, StreamingChatMessageContent

from kernel_builder import create_kernel
from agents_builder import create_agents


# OAuth callback for authentication
# This function is called when the user successfully authenticates with the OAuth provider.


@cl.oauth_callback
async def oauth_callback(
    provider_id: str,
    token: str,
    raw_user_data: Dict[str, str],
    default_user: cl.User,
) -> Optional[cl.User]:
    print(f"OAuth callback for provider {provider_id}")
    default_user.identifier = raw_user_data["mail"]
    default_user.display_name = raw_user_data["displayName"]
    default_user.metadata["user_id"] = raw_user_data["id"]
    default_user.metadata["first_name"] = raw_user_data["givenName"]
    default_user.metadata["job_title"] = raw_user_data["jobTitle"]
    default_user.metadata["office_location"] = raw_user_data["officeLocation"]
    return default_user


# Function to handle chat start event
# This function is called when a new chat session starts.
@cl.on_chat_start
async def on_chat_start():
    # Welcome message
    # app_user = cl.user_session.get("user")
    # await cl.Message(f"Hello **{app_user.metadata["first_name"]}**, how can I help you?").send()

    # Create kernel
    kernel = create_kernel()

    # Create agents    
    agents = create_agents(kernel)

    # Creating the group chat with agents
    group_chat = AgentGroupChat(
        agents=agents,
        termination_strategy=ApprovalTerminationStrategy(
            agents=[agents[3]],
            maximum_iterations=4,
        ),
    )

    # Get the group chat
    cl.user_session.set("group_chat", group_chat)  # type: ignore
    cl.user_session.set("chat_history", ChatHistory())


@cl.on_message  # type: ignore
async def chat(message: cl.Message) -> None:
    group_chat = cl.user_session.get("group_chat")  # type: ignore
    chat_history = cl.user_session.get("chat_history")

    # Add user message to history
    chat_history.add_user_message(message.content)
    print(f"User message: {message.content}")

    # Create a Chainlit message for the response stream
    answer = cl.Message(content="")
    response = cl.Message(content="")
    current_source = None

    await group_chat.add_chat_message(ChatMessageContent(
        role=AuthorRole.USER,
        content=message.content
    ))

    async for msg in group_chat.invoke_stream():
        if isinstance(msg, StreamingChatMessageContent):
            # If source has changed, update the message with a header showing the source
            if current_source != msg.name:
                current_source = msg.name
                if response.content:
                    # Send the current response before starting a new one from different source
                    await response.send()
                    # Process the response content for images
                    #await process_response_content(response)
                    # Create a new response message with source header
                    response = cl.Message(
                        content=f"🤖 **[{current_source}]**\n\n")
                else:
                    # First response, just add the source header
                    response.content = f"🤖 **[{current_source}]**\n\n"

            # Stream the model client response to the user.
            await response.stream_token(msg.content)

    # Add the full assistant response to history
    chat_history.add_assistant_message(answer.content)   
    
    # Send the final message
    await answer.send()

@cl.set_starters  # type: ignore
async def set_starts() -> List[cl.Starter]:
    return [
        cl.Starter(
            label="AI Agent",
            message="Build an AI agent with a FE, BE, and a database.",
        ),
    ]
    
class ApprovalTerminationStrategy(TerminationStrategy):
    """A strategy for determining when an agent should terminate."""

    async def should_agent_terminate(self, agent, history):
        """Check if the agent should terminate."""
        return "approved" in history[-1].content.lower()
