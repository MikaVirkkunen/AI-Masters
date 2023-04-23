from azure.identity import AzureCliCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.resourcegraph import ResourceGraphClient

# Authenticate using the Azure CLI
credential = AzureCliCredential()

# Create the Resource Management and Resource Graph clients
resource_client = ResourceManagementClient(credential, subscription_id)
graph_client = ResourceGraphClient(credential)

# Execute the query to get the list of resources
query = "Resources | project id, type, name, location"
result = graph_client.resources(query)

# Parse the response and display the list of resources
resources = [r.data for r in result]
for resource in resources:
    print(f"{resource['type']} - {resource['name']} - {resource['location']}")
from azure.identity import AzureCliCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.resourcegraph import ResourceGraphClient
from azure.core.exceptions import HttpResponseError

# Authenticate using the Azure CLI
credential = AzureCliCredential()

# Replace with the actual subscription ID
subscription_id = "your-subscription-id"

# Create the Resource Management and Resource Graph clients
resource_client = ResourceManagementClient(credential, subscription_id)
graph_client = ResourceGraphClient(credential)

# Execute the query to get the list of resources
query = "Resources | project id, type, name, location"
try:
    result = graph_client.resources(query)
    resources = [r.data for r in result]
    for resource in resources:
        print(f"{resource['type']} - {resource['name']} - {resource['location']}")
except HttpResponseError as e:
    print(f"Error executing query: {e}")
except Exception as e:
    print(f"Error: {e}")
