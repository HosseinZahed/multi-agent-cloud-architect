from autogen_agentchat.agents import AssistantAgent

def get_agents(model_client):
    """Create the agents for the architecture project."""
    # Create the agents with their respective system messages.
    QueryMaster = AssistantAgent(
        name="QueryMaster",
        model_client=model_client,
        model_client_stream=True,
        system_message="Hello! I'm QueryMaster, here to gather all the necessary information for your Azure architecture project. Please provide as much detail as possible, and I'll ask relevant questions to clarify your requirements."
    )

    ArchiVision = AssistantAgent(
        name="ArchiVision",
        model_client=model_client,
        model_client_stream=True,
        system_message="Greetings! I'm ArchiVision, your high-level Azure architect. Based on the information provided, I'll create a high-level architecture using the best practices from the Azure Architecture Center."
    )

    DetailCraft = AssistantAgent(
        name="DetailCraft",
        model_client=model_client,
        model_client_stream=True,
        system_message="Hi there! I'm DetailCraft, responsible for generating a detailed architecture with the relevant Azure resources. I'll ensure that every component is well-defined and aligned with your high-level architecture."
    )

    FlowSketch = AssistantAgent(
        name="FlowSketch",
        model_client=model_client,
        model_client_stream=True,
        system_message="Hey! I'm FlowSketch, here to bring your architecture to life with Mermaid flowchart diagrams. I'll generate an SVG or PNG output for easy visualization"
    )

    return [QueryMaster, ArchiVision, DetailCraft, FlowSketch]


