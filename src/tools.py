import requests
import base64
import logging
import uuid
import os
import chainlit as cl


@cl.step(type="tool")
async def generate_mermaid_diagram(diagram_code: str, diagram_type: str = 'mermaid', output_format: str = 'png') -> str:
    """
    Generate a diagram using the Kroki API.

    Args:
        diagram_code (str): The diagram code (mermaid, graphviz, etc.)
        diagram_type (str): The type of diagram (mermaid, graphviz, plantuml, etc.)
        output_format (str): The desired output format (png, svg, pdf, etc.)

    Returns:
        str: The filename of the saved diagram
    """
    try:
        url = f"https://kroki.io/{diagram_type}/{output_format}"

        # Send the diagram code directly in the request body
        response = requests.post(url, data=diagram_code)

        # Raise exception for bad responses
        response.raise_for_status()

        # Get the image data
        image_data = response.content

        # Generate a unique filename using UUID
        filename = f"{uuid.uuid4()}.{output_format}"

        # Create the diagrams directory if it doesn't exist
        diagrams_dir = os.path.join(os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))), 'public')
        os.makedirs(diagrams_dir, exist_ok=True)

        # Full path to save the file
        file_path = os.path.join(diagrams_dir, filename)

        # Write the image data to the file
        with open(file_path, 'wb') as f:
            f.write(image_data)

        # Return the filename of the saved diagram        
        print (file_path)
        return filename

    except Exception as e:
        logging.error(f"Error generating diagram with Kroki API: {str(e)}")
        raise


@cl.step(type="tool")
async def get_date() -> str:
    """Get the current date and time."""
    return "2023-10-01T12:00:00Z"  # Placeholder for actual date retrieval logic
