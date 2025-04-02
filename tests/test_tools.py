from src.tools import generate_mermaid_diagram, generate_mermaid_diagram
from unittest.mock import patch, MagicMock
import asyncio
import os
import unittest
import sys
sys.path.append('../')


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


if __name__ == "__main__":
    unittest.main()
