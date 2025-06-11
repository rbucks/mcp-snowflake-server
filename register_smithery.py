import requests
import yaml
import json
from datetime import date, datetime

# Smithery API configuration
API_KEY = "8b0d6e93-2d0b-4a95-b957-8457df0b2d9c"
REGISTRY_URL = "https://registry.smithery.ai/servers"

def load_smithery_config():
    with open("smithery.yaml", "r") as f:
        return yaml.safe_load(f)

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, (date, datetime)):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")

def register_server():
    config = load_smithery_config()
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    # Prepare the server data
    server_data = {
        "qualifiedName": config["name"],
        "displayName": config["displayName"],
        "description": config["description"],
        "connections": config["connections"],
        "security": config["security"],
        "tools": config["tools"]
    }
    
    # Serialize the data with our custom serializer
    json_data = json.dumps(server_data, default=json_serial)
    
    try:
        # First, check if the server exists
        print(f"Checking if server {config['name']} exists...")
        check_response = requests.get(
            f"{REGISTRY_URL}/{config['name']}",
            headers=headers
        )
        print(f"Check response status code: {check_response.status_code}")
        
        if check_response.status_code == 200:
            # Server exists, try to update it
            print(f"Server {config['name']} exists, attempting to update...")
            try:
                response = requests.put(
                    f"{REGISTRY_URL}/{config['name']}",
                    headers=headers,
                    data=json_data
                )
                response.raise_for_status()
                print("Server update successful!")
            except requests.exceptions.RequestException as e:
                print(f"Update failed: {e}")
                print("Attempting to create new server instead...")
                response = requests.post(
                    REGISTRY_URL,
                    headers=headers,
                    data=json_data
                )
                response.raise_for_status()
                print("Server creation successful!")
        elif check_response.status_code == 404:
            # Server doesn't exist, create it
            print(f"Server {config['name']} does not exist, creating...")
            response = requests.post(
                REGISTRY_URL,
                headers=headers,
                data=json_data
            )
            response.raise_for_status()
            print("Server creation successful!")
        else:
            # Unexpected response
            print(f"Unexpected response code: {check_response.status_code}")
            print(f"Response text: {check_response.text}")
            check_response.raise_for_status()
        
        print(json.dumps(response.json(), indent=2))
        
    except requests.exceptions.RequestException as e:
        print(f"Error registering server: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text}")

if __name__ == "__main__":
    register_server() 