import sys
sys.path.append('../')
import asyncio
import unittest
from autogen_core.models import UserMessage
from src.model_provider import create_model_client

class TestModelClient(unittest.TestCase):
    
    def setUp(self):
        # Create a model client for each test
        self.model_client = create_model_client("gpt-4o")
        self.loop = asyncio.get_event_loop()
    
    def tearDown(self):
        # Clean up resources after each test
        self.loop.run_until_complete(self.model_client.close())
    
    def test_model_response(self):
        # Test that the model responds to a simple query
        async def test_async():
            # Create a user message
            user_message = UserMessage(
                content="What's the capital of Denmark?",
                source="user",
                type="UserMessage"
            )
            
            # Send the message to the model client and get the response
            result = await self.model_client.create([user_message])
            
            # Verify we got a response
            self.assertIsNotNone(result)
            self.assertTrue(len(result.content) > 0)
            
            # Print for debugging
            print(f"Model info: {self.model_client.model_info}")
            print(f"Response: {result}")
            
            return result
        
        # Run the async test in the event loop
        result = self.loop.run_until_complete(test_async())
        
        # Additional assertions can be added here if needed
        self.assertIn("Copenhagen", result.content, "Expected 'Copenhagen' in the response")

if __name__ == "__main__":
    unittest.main()
