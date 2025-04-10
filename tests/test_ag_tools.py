import sys
sys.path.append('../')
import zlib
import base64
import unittest
import os
import asyncio
from unittest.mock import patch, MagicMock
from ag_tools_builder import generate_mermaid_diagram, generate_mermaid_diagram, encode_base64

class TestGenerateMermaidDiagram(unittest.TestCase):
    def setUp(self):
        self.valid_mermaid_code = """
        %%{init: {'theme':'neutral'}}%%
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
        self.diagrams_dir = os.path.join(os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))), 'diagrams')
        os.makedirs(self.diagrams_dir, exist_ok=True)

    @patch("src.tools.requests.post")
    def test_generate_mermaid_diagram(self, mock_post):
        # Mock the response content
        mock_post.return_value = MagicMock(
            status_code=200, content=b"fake_image_data")

        # Run the coroutine using asyncio
        filename = asyncio.run(
            generate_mermaid_diagram(self.valid_mermaid_code))

        self.assertTrue(filename.endswith(".png"))

        # Check if the correct URL was called
        mock_post.assert_called_with(
            "https://kroki.io/mermaid/png",
            data=self.valid_mermaid_code
        )

        # Check if file exists and clean up
        file_path = os.path.join(self.diagrams_dir, filename)
        self.assertTrue(os.path.exists(file_path))
        os.remove(file_path)

    @patch("src.tools.requests.post")
    def test_with_different_diagram_type(self, mock_post):
        # Mock the response content
        mock_post.return_value = MagicMock(
            status_code=200, content=b"fake_graphviz_data")

        # Run the coroutine using asyncio
        filename = asyncio.run(generate_mermaid_diagram(
            self.valid_graphviz_code,
            diagram_type="graphviz"
        ))
        self.assertTrue(filename.endswith(".png"))

        # Check if the correct URL was called
        mock_post.assert_called_with(
            "https://kroki.io/graphviz/png",
            data=self.valid_graphviz_code
        )

        # Check if file exists and clean up
        file_path = os.path.join(self.diagrams_dir, filename)
        self.assertTrue(os.path.exists(file_path))
        os.remove(file_path)

    @patch("src.tools.requests.post")
    def test_with_different_output_format(self, mock_post):
        # Mock the response content
        mock_post.return_value = MagicMock(
            status_code=200, content=b"fake_svg_data")

        # Run the coroutine using asyncio
        filename = asyncio.run(generate_mermaid_diagram(
            self.valid_mermaid_code,
            output_format="svg"
        ))
        self.assertTrue(filename.endswith(".svg"))

        # Check if the correct URL was called
        mock_post.assert_called_with(
            "https://kroki.io/mermaid/svg",
            data=self.valid_mermaid_code
        )

        # Check if file exists and clean up
        file_path = os.path.join(self.diagrams_dir, filename)
        self.assertTrue(os.path.exists(file_path))
        os.remove(file_path)

    @patch("src.tools.requests.post")
    def test_request_failure(self, mock_post):
        # Mock a failed request
        mock_post.side_effect = Exception("Request failed")

        # Test exception handling
        with self.assertRaises(Exception):
            asyncio.run(generate_mermaid_diagram(self.valid_mermaid_code))

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
        filename = asyncio.run(generate_mermaid_diagram(
            simple_diagram, output_format="png"))

        # Verify the file exists
        file_path = os.path.join(self.diagrams_dir, filename)
        self.assertTrue(os.path.exists(file_path))

        # Verify file has content (non-zero size)
        self.assertTrue(os.path.getsize(file_path) > 0)

        # Print the filename and size for debugging
        print(f"Generated diagram saved as {filename}")
        print(f"File size: {os.path.getsize(file_path)} bytes")

        # Cleanup
        os.remove(file_path)


class TestEncodeBase64(unittest.TestCase):
    def setUp(self):
        """Set up test cases."""
        self.test_strings = [
            "Hello, World!",
            "",
            "Special characters: !@#$%^&*()",
            "A" * 1000  # A large string
        ]

    @patch('sys.stdin')
    def test_encode_base64(self, mock_stdin):
        """Test the encode_base64 function with various inputs."""
        for test_str in self.test_strings:
            # Mock stdin.read() to return our test string
            mock_stdin.read.return_value = test_str

            # Call the function
            encoded = encode_base64(test_str)

            # Verify it's a string
            self.assertIsInstance(encoded, str)

            # Manually encode to verify correctness
            expected = base64.urlsafe_b64encode(
                zlib.compress(test_str.encode('utf-8'), 9)
            ).decode('ascii')

            # Compare with expected result
            self.assertEqual(encoded, expected)

    @patch('sys.stdin')
    def test_encode_base64_decoding(self, mock_stdin):
        """Test that encoded data can be properly decoded."""
        test_str = "This is a test string for encoding and decoding"
        mock_stdin.read.return_value = test_str

        # Encode the string
        encoded = encode_base64(test_str)

        # Decode and decompress
        decoded_bytes = zlib.decompress(base64.urlsafe_b64decode(encoded))
        decoded = decoded_bytes.decode('utf-8')

        # Original stdin input should match decoded result
        self.assertEqual(test_str, decoded)


if __name__ == "__main__":
    unittest.main()
