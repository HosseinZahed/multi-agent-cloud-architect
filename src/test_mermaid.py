import os
from tools import generate_mermaid_diagram

def test_mermaid_function():
    """Test the generate_mermaid_diagram function with different options."""
    
    # Sample Mermaid diagram
    mermaid_code = """
    graph TD
        A[Cloud Architect] --> B[AWS]
        A --> C[Azure]
        A --> D[GCP]
        B --> E[EC2]
        B --> F[S3]
        C --> G[Azure VMs]
        C --> H[Azure Storage]
        D --> I[Compute Engine]
        D --> J[Cloud Storage]
    """
    
    print("Running mermaid diagram tests...")
    
    # Test 1: Get URL only
    url = generate_mermaid_diagram(mermaid_code)
    print(f"1. Generated URL: {url}")
    
    # Test 2: Get PNG URL 
    png_url = generate_mermaid_diagram(mermaid_code, output_format='png')
    print(f"2. Generated PNG URL: {png_url}")
    
    # Test 3: Save file and get filename
    filename = generate_mermaid_diagram(mermaid_code, save_file=True)
    diagrams_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'diagrams')
    file_path = os.path.join(diagrams_dir, filename)
    print(f"3. Saved diagram to: {file_path}")
    print(f"   File exists: {os.path.exists(file_path)}")
    
    # Test 4: Get SVG binary data
    svg_data = generate_mermaid_diagram(mermaid_code, return_url=False)
    data_size = len(svg_data)
    print(f"4. Retrieved binary data size: {data_size} bytes")
    
    # Test 5: Save as PNG
    png_filename = generate_mermaid_diagram(mermaid_code, output_format='png', save_file=True)
    png_path = os.path.join(diagrams_dir, png_filename)
    print(f"5. Saved PNG diagram to: {png_path}")
    print(f"   File exists: {os.path.exists(png_path)}")
    
    print("\nAll tests completed!")

if __name__ == "__main__":
    test_mermaid_function()
