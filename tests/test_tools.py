import sys
sys.path.append('../')
import unittest
import os
from unittest.mock import patch, MagicMock
from src.tools import generate_mermaid_diagram

class TestGenerateMermaidDiagram(unittest.TestCase):

    def setUp(self):
        self.valid_mermaid_code = """
        flowchart TD
            A[User Interface (Azure App Service)] -->|User Input| B[Azure Functions]
            B -->|Invoke Search| C[Azure Cognitive Search]
            C -->|Retrieve Relevant Docs| D[Azure Blob Storage]
            B -->|Process and Generate| E[Azure OpenAI Service]
            E -->|Return Response| B
            B -->|Send Output| A
            B -->|Log Data| F[Azure Application Insights]
        """
        self.invalid_mermaid_code = 12345  # Not a string
        self.output_format = "png"
        self.invalid_output_format = "jpg"

    @patch("src.tools.requests.get")
    def test_generate_url_only(self, mock_get):
        # Test returning only the URL
        url = generate_mermaid_diagram(self.valid_mermaid_code, return_url=True, save_file=False)
        self.assertTrue(url.startswith("https://mermaid.ink/"))

    @patch("src.tools.requests.get")
    def test_save_file(self, mock_get):
        # Mock the response content
        mock_get.return_value = MagicMock(status_code=200, content=b"fake_image_data")
        
        # Test saving the file
        filename = generate_mermaid_diagram(self.valid_mermaid_code, save_file=True)
        self.assertTrue(filename.endswith(".png"))
        
        # Check if the file was created
        diagrams_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'diagrams')
        file_path = os.path.join(diagrams_dir, filename)
        self.assertTrue(os.path.exists(file_path))
        
        # Cleanup
        os.remove(file_path)

    def test_invalid_mermaid_code(self):
        # Test invalid Mermaid code
        with self.assertRaises(ValueError):
            generate_mermaid_diagram(self.invalid_mermaid_code)

    def test_invalid_output_format(self):
        # Test invalid output format
        with self.assertRaises(ValueError):
            generate_mermaid_diagram(self.valid_mermaid_code, output_format=self.invalid_output_format)

    @patch("src.tools.requests.get")
    def test_return_image_data(self, mock_get):
        # Mock the response content
        mock_get.return_value = MagicMock(status_code=200, content=b"fake_image_data")
        
        # Test returning image data
        image_data = generate_mermaid_diagram(self.valid_mermaid_code, return_url=False, save_file=False)
        self.assertEqual(image_data, b"fake_image_data")

    @patch("src.tools.requests.get")
    def test_request_failure(self, mock_get):
        # Mock a failed request
        mock_get.side_effect = Exception("Request failed")
        
        # Test exception handling
        with self.assertRaises(Exception):
            generate_mermaid_diagram(self.valid_mermaid_code)

if __name__ == "__main__":
    unittest.main()
