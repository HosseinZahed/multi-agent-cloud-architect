import asyncio
from autogen_core.models import UserMessage
from model_provider import create_model_client

async def main():
    # Create a model client
    model_client = create_model_client("gpt-4o")
    try:
        # Print model information
        print(model_client.model_info)
        
        # Create a user message
        user_message = UserMessage(
            content="What's the capital of Denmark?",
            source="user",
            type="UserMessage"
        )

        # Send the message to the model client and get the response
        result = await model_client.create([user_message])

        # Print the response
        print(result)
    finally:
        # Close the model client
        await model_client.close()

if __name__ == "__main__":
    asyncio.run(main())
