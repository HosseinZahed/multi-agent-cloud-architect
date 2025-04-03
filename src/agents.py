from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from model_provider import create_model_client
from autogen_core import CancellationToken
import chainlit as cl
from tools import generate_mermaid_diagram, get_date


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
                cl.Action(name="approve", label="Approve",
                          payload={"value": "approve"}),
                cl.Action(name="reject", label="Reject",
                          payload={"value": "reject"}),
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

    # Create the user approval agent.
    user_approval_agent = UserProxyAgent(
        name="user_approval_agent",
        input_func=user_action_func,
        description="A human user to approve or reject the architecture.",
    )

    # Create the questioner agent.
    questioner_agent = AssistantAgent(
        name="questioner_agent",
        model_client=create_model_client("gpt-4o-mini"),
        model_client_stream=True,
        system_message="""
            You are an Azure requirements specialist responsible for gathering essential information about the user's cloud architecture project. Your role is to:
            
            1. Ask targeted questions (maximum 5) to understand the user's Azure project requirements
            2. Focus on technical and business requirements that will influence architectural decisions
            3. Cover key areas such as:
               - Project objectives and business goals
               - Workload characteristics and performance needs
               - Security and compliance requirements
               - Budget constraints and cost considerations
               - Existing infrastructure and integration requirements
            
            Ensure questions are clear, relevant, and build upon previous responses. Do not request any sensitive information such as credentials, personal data, or specific security configurations.
            Keep the conversation professional and focused on gathering actionable requirements for architectural planning.
        """,
    )

    # Create the architect agent.
    architect_agent = AssistantAgent(
        name="architect_agent",
        model_client=create_model_client("gpt-4o-mini"),
        model_client_stream=True,
        system_message="""
            You are a professional Azure Solutions Architect with expertise in cloud design principles. When users present requirements for an Azure solution, please:
            
            1. Create a high-level architecture recommendation aligned with Microsoft's best practices from:
               - Azure Well-Architected Framework 
               - Azure Architecture Center
               - Cloud Adoption Framework
            
            2. Include the following in your response:
               - Architecture overview and key components
               - Security and compliance considerations
               - Cost optimization strategies
               - Scalability and performance aspects
               - Reliability and business continuity measures          
            
            3. Provide links to relevant Azure documentation and resources for further guidance.
            
            Keep responses clear, concise, and actionable while following Azure architectural best practices.
        """,
    )

    # Create the diagram agent.
    diagram_agent = AssistantAgent(
        name="diagram_agent",
        model_client=create_model_client(
            "mistral-small-2503",
            function_calling=True,
            json_output=True),
        tools=[generate_mermaid_diagram],
        reflect_on_tool_use=True,
        model_client_stream=True,
        system_message="""
            You're a Mermaid diagram generation specialist working with Azure architectures.
            
            When presented with a high-level architecture from the architect agent:
            - Analyze the architecture components and their connections
            - Create a simple, focused flowchart using Mermaid syntax
            - Exclude subgraphs, parentheses, special characters and symbols
            - Include only essential components, services, and data flows            
            - Use clear, descriptive node labels and meaningful connection descriptions
            - Ensure diagram is technically accurate and follows Azure architecture patterns
            - Exclude any styling, CSS formatting, or comments from the diagram code            
            - Generate clean, minimal code that will render correctly in standard Mermaid viewers
        """,
    )

    # Create the illustrator agent.
    illustrator_agent = AssistantAgent(
        name="illustrator_agent",
        model_client=create_model_client(
            "mistral-small-2503",
            function_calling=True,
            json_output=True),
        tools=[generate_mermaid_diagram],
        reflect_on_tool_use=True,
        model_client_stream=True,
        system_message="""
            You're a diagram illustrator specialist.
            When presented with Mermaid code from the diagram agent:
            - Keep new lines and indentation from the provided code
            - Illustrate the diagram using the provided tool.            
            - If the answer from the tool is valid, return the diagram filename.
            - If the answer from the tool is invalid, return an error message.
        """,
    )

    # Create the architect agent."""
    calendar_agent = AssistantAgent(
        name="calendar_agent",
        model_client=create_model_client(
            "mistral-small-2503",
            function_calling=True,
            json_output=True),
        tools=[get_date],
        reflect_on_tool_use=True,
        model_client_stream=True,
        system_message="""            
            You're a helpful assistant.
        """,
    )

    return [
        #questioner_agent,
        # user_input_agent,
        architect_agent,
        diagram_agent,
        illustrator_agent,
        # user_approval_agent

        # calendar_agent,
        # user_approval_agent,
    ]
