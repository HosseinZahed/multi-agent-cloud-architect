import os
from dotenv import load_dotenv
from semantic_kernel.kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from openai import AsyncOpenAI

# Load environment variables from .env file
load_dotenv(override=True)

def create_kernel() -> Kernel:
    """
    Create a kernel with Azure OpenAI service.
    """
    kernel = Kernel()

    client = AsyncOpenAI(api_key=os.environ["GITHUB_TOKEN"],
                         base_url=os.environ["AZURE_OPENAI_ENDPOINT"])

    kernel.add_service(
        AzureChatCompletion(
            ai_model_id="gpt-35-turbo",
            async_client=client,
            service_id=service_id
        )
    )

    return kernel

def create_kernel_with_chat_completion(service_id: str, model_name: str) -> Kernel:
    kernel = Kernel()
    service_id = "agent"

    client = AsyncOpenAI(api_key=os.environ["GITHUB_TOKEN"],
                         base_url=os.environ["AZURE_OPENAI_ENDPOINT"])

    kernel.add_service(
        AzureChatCompletion(
            ai_model_id=model_name,
            async_client=client,
            service_id=service_id
        )
    )

    return kernel
