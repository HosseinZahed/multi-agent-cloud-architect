import os
import asyncio
from autogen_ext.models.openai import AzureOpenAIChatCompletionClient
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.agents import UserProxyAgent

# Set Azure OpenAI configuration
api_key = "7yehBVCtjAKfBJFLnuXkV3hljLBn6mzR464rUPRwGswuszJe8vasJQQJ99BCACfhMk5XJ3w3AAAAACOGmQjN"
azure_endpoint = "https://ai-srv-demo-hz.openai.azure.com/"
api_version = "2024-10-21"  # Update to the version you're using
deployment_name = "gpt-4o-mini"  # Your Azure OpenAI deployment name
model_name = "gpt-4o-mini"  # Your Azure OpenAI model name

# Create an Azure OpenAI chat completion client
client = AzureOpenAIChatCompletionClient(
    api_key=api_key,
    azure_endpoint=azure_endpoint,
    api_version=api_version,
    azure_deployment=deployment_name,
    model=model_name,
    #azure_api_type="azure",
    temperature=0.7,
    timeout=600
)

async def main() -> None:
    agent = AssistantAgent("assistant", client)
    print(await agent.run(task="Say 'Hello World!'"))

asyncio.run(main())