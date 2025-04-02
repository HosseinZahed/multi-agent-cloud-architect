import requests
import base64
import logging
import uuid
import os
import chainlit as cl
from typing import Dict, Any


@cl.step(type="tool")
async def generate_mermaid_diagram(diagram_code: str, diagram_type: str = 'mermaid', output_format: str = 'png') -> Dict[str, Any]:
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
        # Get the current step to associate the image with
        current_step = cl.context.current_step

        url = f"https://kroki.io/{diagram_type}/{output_format}"
        # url = f"http://localhost:1234/{diagram_type}/{output_format}"

        # Send the diagram code directly in the request body
        response = requests.post(url, data=diagram_code)

        # Raise exception for bad responses
        response.raise_for_status()

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

        # Return a JSON-compatible dictionary with the result
        return {
            "filename": filename,
            "file_path": file_path,
            "diagram_type": diagram_type,
            "output_format": output_format,
            "status": "success"
        }

    except Exception as e:
        error_message = f"Error generating diagram with Kroki API: {str(e)}"
        logging.error(error_message)
        # Return error information as JSON
        return {
            "status": "error",
            "message": error_message,
            "error": str(e)
        }


@cl.step(type="tool")
async def validate_mermaid_code(mermaid_code: str, output_format: str = 'png') -> str:
    """
        Validate the syntax of the provided Mermaid code using the Mermaid API.
    """
    # Clean the Mermaid code
    mermaid_code = clean_mermaid_code(mermaid_code)
    
    # Encode the Mermaid code in base64
    encoded_mermaid_code = base64.b64encode(mermaid_code.encode('utf-8')).decode('utf-8')
    print(f"Encoded Mermaid code: {encoded_mermaid_code}")
    
    
    api_url = f"https://mermaid.ink/img/pako:{encoded_mermaid_code}"

    try:    
        response = requests.get(api_url)
        # Raise exception for bad responses        
        response.raise_for_status()
        
        # Save the image to a file
        #filename = save_image(response, output_format)
        filename = f"{uuid.uuid4()}.{output_format}"
        
        # Return the result as JSON
        return {
            "filename": filename,            
            "output_format": output_format,
            "valid": True
        }
        
    except Exception as e:
        logging.error(str(e))
        # Return error information as JSON
        return {            
            "error": str(e),
            "valid": False
        }

def clean_mermaid_code(mermaid_code: str) -> str:
    """
        Clean the Mermaid code by removing unnecessary whitespace and comments.
    """
    # Remove leading and trailing whitespace
    mermaid_code = mermaid_code.strip()
    
    # Remove parentheses and comments
    mermaid_code = mermaid_code.replace("(", "").replace(")", "").replace("//", "").replace("#", "")
    
    


def save_image(response, output_format: str = 'png') -> str:
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


@cl.step(type="tool")
async def get_date() -> str:
    """Get the current date and time."""
    return "2023-10-01T12:00:00Z"  # Placeholder for actual date retrieval logic
