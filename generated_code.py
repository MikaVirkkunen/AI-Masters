# Import required libraries and modules
from azure.identity import ClientSecretCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.subscription import SubscriptionClient
from azure.graphrbac import GraphRbacManagementClient
import openai
from docx import Document
from docx.shared import Inches
import matplotlib.pyplot as plt
import seaborn as sns

# Functions for authentication, data retrieval, summary generation, visualization, and document creation

# ... (all functions from previous steps)

def main():
    # Authenticate and connect to Azure
    # ... (code from step 1)

    # Retrieve data
    # ... (code from step 2)

    # Generate summaries using Azure OpenAI
    summaries = {}
    for category, data in [('Azure Active Directory', aad_users),
                           ('Subscriptions', subscriptions),
                           ('Networking', virtual_networks),
                           ('Management Groups', management_groups),
                           ('Policies', policy_definitions)]:
        prompt = f"Please provide a concise summary of the following {category} data:\n{data}"
        summaries[category] = generate_summary(prompt)

    # Create visualizations
    # ... (code for creating visualizations)

    # Add visualizations to the summaries dictionary
    summaries['Subscriptions'].append('resources_per_subscription.png')
    summaries['Networking'].append('virtual_networks_distribution.png')

    # Create the Word document
    create_word_document(summaries)

if __name__ == "__main__":
    main()

# Import required libraries and modules
from azure.identity import ClientSecretCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.subscription import SubscriptionClient
from azure.graphrbac import GraphRbacManagementClient
import openai
from docx import Document
from docx.shared import Inches
import matplotlib.pyplot as plt
import seaborn as sns

# Functions for authentication, data retrieval, summary generation, visualization, and document creation

# ... (all functions from previous steps)

def main():
    # Authenticate and connect to Azure
    # ... (code from step 1)

    # Retrieve data
    # ... (code from step 2)

    # Generate summaries using Azure OpenAI
    summaries = {}
    for category, data in [('Azure Active Directory', aad_users),
                           ('Subscriptions', subscriptions),
                           ('Networking', virtual_networks),
                           ('Management Groups', management_groups),
                           ('Policies', policy_definitions)]:
        prompt = f"Please provide a concise summary of the following {category} data:\n{data}"
        summaries[category] = generate_summary(prompt)

    # Create visualizations
    # ... (code for creating visualizations)

    # Add visualizations to the summaries dictionary
    summaries['Subscriptions'].append('resources_per_subscription.png')
    summaries['Networking'].append('virtual_networks_distribution.png')

    # Create the Word document
    create_word_document(summaries)

if __name__ == "__main__":
    main()