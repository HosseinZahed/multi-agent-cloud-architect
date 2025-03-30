import requests
import base64
import logging
import uuid
import os

def generate_mermaid_diagram(mermaid_code, output_format='png', return_url=True, save_file=False):
    """
    Generate a URL for rendering a Mermaid diagram using mermaid.ink.
    
    Args:
        mermaid_code (str): The Mermaid diagram code as string
        output_format (str): The desired output format ('svg' or 'png')
        return_url (bool): If True, returns the URL. If False, fetches and returns the image data
        save_file (bool): If True, saves the diagram to the diagrams folder
    
    Returns:
        str: Either the URL to the rendered diagram, the filename of the saved diagram, 
             or the actual image data
    """
    try:
        # Base64 encode the diagram code and make it URL safe
        encoded_diagram = base64.urlsafe_b64encode(mermaid_code.encode('utf-8')).decode('utf-8')
        
        # Construct the URL based on the requested format
        if output_format.lower() == 'svg':
            url = f"https://mermaid.ink/svg/{encoded_diagram}"
        elif output_format.lower() == 'png':
            url = f"https://mermaid.ink/img/{encoded_diagram}"
        else:
            raise ValueError(f"Unsupported output format: {output_format}. Use 'svg' or 'png'.")
        
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
            filename = f"{uuid.uuid4()}.{output_format.lower()}"
            
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
