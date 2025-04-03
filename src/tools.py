import requests
from requests.models import Response
import base64
import logging
import uuid
import os
import base64
import zlib
import chainlit as cl
from typing import Dict, Any


@cl.step(type="tool")
async def generate_mermaid_diagram(
        diagram_code: str,
        diagram_type: str = 'mermaid',
        output_format: str = 'png') -> Dict[str, Any]:
    """
    Generate a diagram using the Kroki API.

    Args:
        diagram_code (str): The diagram code (mermaid, graphviz, etc.)
        diagram_type (str): The type of diagram (mermaid, graphviz, plantuml, etc.)
        output_format (str): The desired output format (png, svg, pdf, etc.)

    Returns:
        Dict[str, Any]: A dictionary containing the filename and status information
    """
    try:
        
        # Sanitize the diagram code
        diagram_code = sanitize_mermaid_code(diagram_code)
        

        # Set the Kroki API URL based on the diagram type and output format
        url = f"https://kroki.io/{diagram_type}/{output_format}"

        # Send the diagram code directly in the request body
        response = requests.post(url, data=diagram_code)

        # Raise exception for bad responses
        response.raise_for_status()

        # Save the image to a file
        filename = save_image(response, output_format)

        # Return a JSON-compatible dictionary with the result
        return {
            "filename": filename,
            "valid": True
        }

    except Exception as e:
        error_message = f"Error generating diagram with Kroki API: {str(e)}"
        logging.error(error_message)
        # Return error information as JSON
        return {
            "message": error_message,
            "error": str(e),
            "valid": False
        }


# @cl.step(type="tool")
def generate_mermaid_diagram_encoded(
        mermaid_code: str,
        output_format: str = 'png') -> str:
    """
        Generate a diagram using the Kroki API.
        Args:
            mermaid_code (str): The Mermaid diagram code.
            output_format (str): The desired output format (png, svg, pdf, etc.)
        Returns:
            str: The filename of the generated diagram.       
    """
    # Encode the Mermaid code in base64
    encoded_mermaid_code = encode_base64(mermaid_code)
    print(f"Encoded Mermaid code: {encoded_mermaid_code}")

    api_url = f"https://kroki.io/mermaid/png"

    try:
        response = requests.get(api_url)
        # Raise exception for bad responses
        response.raise_for_status()

        # Save the image to a file
        filename = save_image(response, output_format)
        # filename = f"{uuid.uuid4()}.{output_format}"

        # Return the result as JSON
        return {
            "filename": filename,
            "valid": True
        }

    except Exception as e:
        logging.error(str(e))
        # Return error information as JSON
        return {
            "error": str(e),
            "valid": False
        }


def sanitize_mermaid_code(mermaid_code: str) -> str:
    """
        Sanitize the Mermaid code by removing unnecessary whitespace and comments.
    """
    # Remove parentheses and comments
    if(mermaid_code.count("\n") == 0):
        mermaid_code = mermaid_code.replace("     ", "\n     ")    
    mermaid_code = mermaid_code.replace("(", "").replace(
        ")", "").replace("//", "").replace("#", "")    
    return mermaid_code


def save_image(response: Response, output_format: str = 'png') -> str:
    """
        Save the image data to a file and return the filename.
    """
    # Get the image data
    image_data = response.content

    # Generate a unique filename using UUID
    filename = f"{uuid.uuid4()}.{output_format}"

    # Get the path to the src directory and create .files folder if it doesn't exist
    src_dir = os.path.dirname(os.path.abspath(__file__))
    files_dir = os.path.join(src_dir, '.files')
    os.makedirs(files_dir, exist_ok=True)

    # Set the file path inside the .files directory
    file_path = os.path.join(files_dir, filename)

    # Write the image data to the file
    with open(file_path, 'wb') as f:
        f.write(image_data)

    return filename


def encode_base64(data: str) -> str:
    """
        Encode the given data in base64.
    """
    return base64.urlsafe_b64encode(zlib.compress(data.encode('utf-8'), 9)).decode('ascii')


@cl.step(type="tool")
async def get_date() -> str:
    """Get the current date and time."""
    return "2023-10-01T12:00:00Z"  # Placeholder for actual date retrieval logic
