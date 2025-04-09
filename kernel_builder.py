import os
import semantic_kernel as sk
from openai import AsyncOpenAI
from semantic_kernel.connectors.ai import FunctionChoiceBehavior
from semantic_kernel.kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion, OpenAIChatPromptExecutionSettings


# Create a kernel with Azure OpenAI service
def create_kernel() -> Kernel:
    """
    Create a kernel with the required agents.
    """
    # Create a kernel with Azure OpenAI service.
    client = AsyncOpenAI(api_key=os.environ["GITHUB_TOKEN"],
                         base_url=os.environ["AZURE_OPENAI_ENDPOINT"])

    # Define the request settings for the OpenAI API
    # request_settings = OpenAIChatPromptExecutionSettings(
    #     function_choice_behavior=FunctionChoiceBehavior.Auto(
    #         filters={"excluded_plugins": ["ChatBot"]})
    # )

    # Create a kernel with the client and request settings
    kernel = sk.Kernel()
    kernel.add_service(OpenAIChatCompletion(
        ai_model_id="gpt-4o-mini",
        async_client=client,
        service_id="agent-service"
        )
    )

    return kernel
