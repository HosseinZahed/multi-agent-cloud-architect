from tools import encode_base64, generate_mermaid_diagram
import asyncio

diagram = """
graph TD
    Frontend --> Backend
    Backend --> AIModel
    Backend --> Database
    Frontend --> APIManagement
    APIManagement --> Backend
    Backend --> APIManagement
    Database --> GeoRedundancy
    GeoRedundancy --> TrafficManager
    TrafficManager --> Frontend
    Frontend --> LoadBalancer
    LoadBalancer --> Backend
    Backend --> Cache
    Cache --> Database
    Frontend --> Monitoring
    Monitoring --> Backend
    Monitoring --> Database
    Monitoring --> AIModel
    Backend --> IdentityManagement
    Database --> Backup
    Backend --> CostManagement
    Backend --> Scaling
    Backend --> Compliance
    Backend --> Security

"""

#encoded_diagram = encode_base64(diagram)
#print(f"Encoded diagram: {encoded_diagram}")

filename = generate_mermaid_diagram(diagram, output_format='png')
print(f"Filename: {filename}")