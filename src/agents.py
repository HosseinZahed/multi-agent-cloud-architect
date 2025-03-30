from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from model_provider import create_model_client
from autogen_core import CancellationToken
import chainlit as cl
from tools import generate_mermaid_diagram

async def user_input_func(prompt: str, cancellation_token: CancellationToken | None = None) -> str:
    """Get user input from the UI for the user proxy agent."""
    try:        
        prompt = "Please provide answers to the questions."
        response = await cl.AskUserMessage(content=prompt, timeout=600).send()
    except TimeoutError:
        return "User did not provide any input within the time limit."    
    if response:
        return response["output"]  # type: ignore
    else:
        return "User did not provide any input."


async def user_action_func(prompt: str, cancellation_token: CancellationToken | None = None) -> str:
    """Get user action from the UI for the user proxy agent."""
    try:
        response = await cl.AskActionMessage(
            content="Pick an action",
            actions=[
                cl.Action(name="approve", label="Approve", payload={"value": "approve"}),
                cl.Action(name="reject", label="Reject", payload={"value": "reject"}),
            ],
        ).send()
    except TimeoutError:
        return "User did not provide any input within the time limit."
    if response and response.get("payload"):  # type: ignore
        if response.get("payload").get("value") == "approve":  # type: ignore
            return "APPROVE."  # This is the termination condition.
        else:
            return "REJECT."
    else:
        return "User did not provide any input."


def get_participants() -> list[str]:
    """Get the list of participants in the conversation."""
    
    # Create the user input agent.
    user_input_agent = UserProxyAgent(
        name="user_input_agent",
        input_func=user_input_func,        
        description="A human user to provide input to the agent.",
    )

    # Create the user approval agent."""    
    user_approval_agent = UserProxyAgent(
        name="user_approval_agent",
        input_func=user_action_func,
        description="A human user to approve or reject the architecture.",
    )
    
    # Create the questioner agent."""    
    questioner_agent = AssistantAgent(
        name="questioner_agent",
        model_client=create_model_client("gpt-4o-mini"),
        model_client_stream=True,
        system_message=
        """
            You're responsible for asking questions to gather information
            about the user's Azure architecture project. Your goal is to 
            ask relevant questions to clarify the user's requirements and 
            gather all necessary information. Max out at 5 questions.
            Do not ask for any sensitive information.
            Use emojis to make the conversation more engaging.
        """,
    )

    # Create the architect agent."""    
    architect_agent = AssistantAgent(
        name="architect_agent",
        model_client=create_model_client("gpt-4o-mini"),
        model_client_stream=True,
        system_message=
        """
            You're a professional Azure architect. Based on the information 
            provided by the user, create a high-level architecture using the
            best practices from the Azure Architecture Center and the Cloud Adoption Framework.
            Provide links to relevant resources and documentation.
            Your response should be clear and concise, and it should include emojis
            to make the conversation more engaging.
        """,
    )
    
    # Create the illustrator agent."""
    illustrator_agent = AssistantAgent(
        name="illustrator_agent",
        model_client=create_model_client("gpt-4o"),
        #tools=[generate_mermaid_diagram],
        model_client_stream=True,
        system_message=
        """
            You are a Mermaid flowchart diagram generator. Using the high-level 
            architecture provided by the architect agent, create a clear and 
            visually appealing flowchart in Mermaid syntax. Utilize the specified
            tool to generate the diagram. You need to pass the diagram code to the
            tool and return the filename produced by the tool's output
            Whenever you respond, ensure that your output is a JSON object with 
            the following keys:
                "text": A string containing the main response message.
                "image_filename": A string representing the name of file name produced by the tool's output.
            Ensure that the "image_filename" points to a valid image file. Do not deviate from this format."        
        """,
    )
    
    return [
        questioner_agent, 
        user_input_agent,
        architect_agent,
        illustrator_agent,
        user_approval_agent
    ]