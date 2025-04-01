import sys
sys.path.append('../')
import unittest
import os
import asyncio
from unittest.mock import patch, MagicMock
from src.tools import generate_mermaid_diagram, generate_mermaid_diagram2

# class TestGenerateMermaidDiagram(unittest.TestCase):    
#     def setUp(self):
#         self.valid_mermaid_code = """
#         flowchart TD
#             A[User Interface] -->|User Input| B[Azure Functions]
#             B -->|Invoke Search| C[Azure Cognitive Search]
#             C -->|Retrieve Relevant Docs| D[Azure Blob Storage]
#             B -->|Process and Generate| E[Azure OpenAI Service]
#             E -->|Return Response| B
#             B -->|Send Output| A
#             B -->|Log Data| F[Azure Application Insights]
#         """
#         self.invalid_mermaid_code = 12345  # Not a string
#         self.output_format = "png"
#         self.invalid_output_format = "jpg"

#     @patch("src.tools.requests.get")
#     def test_generate_url_only(self, mock_get):
#         # Test returning only the URL
#         url = generate_mermaid_diagram(self.valid_mermaid_code, return_url=True, save_file=False)
#         print(url)
#         self.assertTrue(url.startswith("https://mermaid.ink/"))

#     @patch("src.tools.requests.get")
#     def test_save_file(self, mock_get):
#         # Mock the response content
#         mock_get.return_value = MagicMock(status_code=200, content=b"fake_image_data")
        
#         # Test saving the file
#         filename = generate_mermaid_diagram(self.valid_mermaid_code, save_file=True)
#         self.assertTrue(filename.endswith(".png"))
        
#         # Check if the file was created
#         diagrams_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'diagrams')
#         file_path = os.path.join(diagrams_dir, filename)
#         self.assertTrue(os.path.exists(file_path))
        
#         # Cleanup
#         os.remove(file_path)

#     def test_invalid_mermaid_code(self):
#         # Test invalid Mermaid code
#         with self.assertRaises(ValueError):
#             generate_mermaid_diagram(self.invalid_mermaid_code)

#     def test_invalid_output_format(self):
#         # Test invalid output format
#         with self.assertRaises(ValueError):
#             generate_mermaid_diagram(self.valid_mermaid_code, output_format=self.invalid_output_format)

#     @patch("src.tools.requests.get")
#     def test_return_image_data(self, mock_get):
#         # Mock the response content
#         mock_get.return_value = MagicMock(status_code=200, content=b"fake_image_data")
        
#         # Test returning image data
#         image_data = generate_mermaid_diagram(self.valid_mermaid_code, return_url=False, save_file=False)
#         self.assertEqual(image_data, b"fake_image_data")

#     @patch("src.tools.requests.get")
#     def test_request_failure(self, mock_get):
#         # Mock a failed request
#         mock_get.side_effect = Exception("Request failed")
        
#         # Test exception handling
#         with self.assertRaises(Exception):
#             generate_mermaid_diagram(self.valid_mermaid_code)
    
#     @patch('chainlit.context.init_context')
#     def mock_init_context(*args, **kwargs):
#         pass

class TestGenerateMermaidDiagram2(unittest.TestCase):
    def setUp(self):
        self.valid_mermaid_code = """
        flowchart TD
            A[User Interface] -->|User Input| B[Azure Functions]
            B -->|Invoke Search| C[Azure Cognitive Search]
            C -->|Retrieve Relevant Docs| D[Azure Blob Storage]
            B -->|Process and Generate| E[Azure OpenAI Service]
            E -->|Return Response| B
            B -->|Send Output| A
            B -->|Log Data| F[Azure Application Insights]
        """
        self.valid_graphviz_code = """
        digraph G {
            A -> B;
            B -> C;
            C -> D;
        }
        """
        self.output_formats = ["png", "svg"]

    @patch("src.tools.requests.post")
    def test_generate_mermaid_diagram(self, mock_post):
        # Mock the response content
        mock_post.return_value = MagicMock(status_code=200, content=b"fake_image_data")
        
        # Run the coroutine using asyncio
        image_data = asyncio.run(generate_mermaid_diagram2(self.valid_mermaid_code))
       
        self.assertEqual(image_data, b"fake_image_data")
        
        # Check if the correct URL was called
        mock_post.assert_called_with(
            "https://kroki.io/mermaid/png",
            data=self.valid_mermaid_code
        )

    @patch("src.tools.requests.post")
    def test_with_different_diagram_type(self, mock_post):
        # Mock the response content
        mock_post.return_value = MagicMock(status_code=200, content=b"fake_graphviz_data")
        
        # Run the coroutine using asyncio
        image_data = asyncio.run(generate_mermaid_diagram2(
            self.valid_graphviz_code, 
            diagram_type="graphviz"
        ))
        self.assertEqual(image_data, b"fake_graphviz_data")
        
        # Check if the correct URL was called
        mock_post.assert_called_with(
            "https://kroki.io/graphviz/png",
            data=self.valid_graphviz_code
        )

    @patch("src.tools.requests.post")
    def test_with_different_output_format(self, mock_post):
        # Mock the response content
        mock_post.return_value = MagicMock(status_code=200, content=b"fake_svg_data")
        
        # Run the coroutine using asyncio
        image_data = asyncio.run(generate_mermaid_diagram2(
            self.valid_mermaid_code, 
            output_format="svg"
        ))
        self.assertEqual(image_data, b"fake_svg_data")
        
        # Check if the correct URL was called
        mock_post.assert_called_with(
            "https://kroki.io/mermaid/svg",
            data=self.valid_mermaid_code
        )

    @patch("src.tools.requests.post")
    def test_request_failure(self, mock_post):
        # Mock a failed request
        mock_post.side_effect = Exception("Request failed")
        
        # Test exception handling
        with self.assertRaises(Exception):
            asyncio.run(generate_mermaid_diagram2(self.valid_mermaid_code))

    def test_real_api_call(self):
        """Test with a real API call to verify integration with Kroki."""
        simple_diagram = """
        graph TD;
            A-->B;
            A-->C;
            B-->D;
            C-->D;
        """
        
        # Make a real API call (no mocking) - using PNG format instead of SVG
        result = asyncio.run(generate_mermaid_diagram2(simple_diagram, output_format="png"))
        
        # Verify we got a valid response (PNG data should start with the PNG signature)
        self.assertTrue(
            result.startswith(b"\x89PNG"),
            "Response doesn't appear to be valid PNG data"
        )
        
        # Print the size of the returned data for debugging
        print(f"Received {len(result)} bytes of PNG data from Kroki API")
        
        # Optionally save the diagram to verify visually
        diagrams_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'diagrams')
        os.makedirs(diagrams_dir, exist_ok=True)
        test_file_path = os.path.join(diagrams_dir, "test_kroki_api.png")
        
        with open(test_file_path, 'wb') as f:
            f.write(result)
        
        print(f"Saved test diagram to {test_file_path}")
        
        # Cleanup
        os.remove(test_file_path)

if __name__ == "__main__":
    unittest.main()
