from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from model_provider import create_model_client
from autogen_core import CancellationToken
import chainlit as cl
from tools import generate_mermaid_diagram, validate_mermaid_code, get_date


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

    # Create the illustrator agent.
    diagram_agent = AssistantAgent(
        name="diagram_agent",
        model_client=create_model_client(
            "mistral-small-2503",
            function_calling=True,
            json_output=True),
        tools=[validate_mermaid_code],
        reflect_on_tool_use=True,
        model_client_stream=True,
        system_message="""
            You are a diagram generation specialist. When presented with a high-level architecture from the architect agent:
            1. Provide the Mermaid code to generate the diagram consider the following:
               - Use the Mermaid syntax to represent the architecture.
               - Include all components and their relationships as described in the architecture.
               - Ensure the diagram is clear, concise, and easy to understand.
               - Use simple and consistent labels for components and connections.
               - Avoid advanced or complex Mermaid features that may hinder readability.
            2. Use the provided tool to validate the generated Mermaid code.
            3. If the code is invalid, fix the issues and regenerate it until it is valid.
            4. Only after the code is valid, generate the code as the output.
            
            If there are any syntax errors or issues with the Mermaid code, provide specific feedback on what needs to be corrected.
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
            You are a diagram generation specialist. When presented with Mermaid code from an Azure architecture design:
            
            1. Use the appropriate tool to render the Mermaid diagram
            2. Provide the exact filename of the saved diagram in your response
            3. Confirm successful generation of the diagram
            
            If there are any syntax errors or issues with the Mermaid code, provide specific feedback on what needs to be corrected.
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
        questioner_agent,
        # user_input_agent,
        architect_agent,
        diagram_agent,
        # illustrator_agent,
        # user_approval_agent

        # calendar_agent,
        # user_approval_agent,
    ]
