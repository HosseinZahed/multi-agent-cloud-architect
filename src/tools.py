import requests
import base64
import logging
import uuid
import os
import chainlit as cl

@cl.step(type="tool")
def generate_mermaid_diagram(mermaid_code: str, output_format: str = 'png', return_url: bool = True, save_file: bool = True) -> str:
    """
    Generate a URL for rendering a Mermaid diagram using mermaid.ink.
    
    Args:
        mermaid_code (str): The Mermaid diagram code as string
        output_format (str): The desired output format ('svg' or 'png')
        return_url (bool): If True, returns the URL. If False, fetches and returns the image data
        save_file (bool): If True, saves the diagram to the diagrams folder
    
    Returns:
        str: Return the name of the saved file
    """
    try:
        # Validate mermaid_code
        if not mermaid_code or not isinstance(mermaid_code, str):
            raise ValueError("Invalid Mermaid code. It must be a non-empty string.")
        
        # Validate output_format
        output_format = output_format.lower()
        if output_format not in ['svg', 'png']:
            raise ValueError(f"Unsupported output format: {output_format}. Use 'svg' or 'png'.")
        
        # Base64 encode the diagram code and make it URL safe
        encoded_diagram = base64.urlsafe_b64encode(mermaid_code.encode('utf-8')).decode('utf-8')
        
        # Construct the URL based on the requested format
        url = f"https://mermaid.ink/{'svg' if output_format == 'svg' else 'img'}/{encoded_diagram}"
        
        # If we only need the URL and don't need to save, return it
        if return_url and not save_file:
            return url
        
        # Get the image data
        response = requests.get(url)
        response.raise_for_status()  # Raise exception for bad responses
        image_data = response.content
        
        # If we need to save the file
        if save_file:
            # Generate a unique filename using UUID
            filename = f"{uuid.uuid4()}.{output_format}"
            
            # Create the diagrams directory if it doesn't exist
            diagrams_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'diagrams')
            os.makedirs(diagrams_dir, exist_ok=True)
            
            # Full path to save the file
            file_path = os.path.join(diagrams_dir, filename)
            
            # Write the image data to the file
            with open(file_path, 'wb') as f:
                f.write(image_data)
            
            # Return the filename of the saved diagram
            return filename
        
        # Otherwise, return the image data
        return image_data
        
    except Exception as e:
        logging.error(f"Error generating Mermaid diagram: {str(e)}")
        raise

@cl.step(type="tool")
async def get_date() -> str:
    """Get the current date and time."""    
    return "2023-10-01T12:00:00Z"  # Placeholder for actual date retrieval logic