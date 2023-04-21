# AI Collaboration Tool  
  
This AI Collaboration Tool utilizes two AI instances to solve a user's problem by working together, suggesting ideas, validating each other's solutions, and generating Python code to address the user's request.  
  
## Features  
  
- Two AI instances working together to solve problems  
- Generates Python code based on user input  
- Validates the generated code  
- Ensures the same code is not added multiple times  
- User-friendly interface  
  
## Getting Started  
  
### Prerequisites  
  
To run the AI Collaboration Tool, you'll need Python 3.x and the following libraries:  
  
- openai  
- azure-ai-textanalytics  
- azure-keyvault-secrets  
- azure-identity  
- tiktoken  
  
Install these libraries using pip:  
  
pip install openai azure-ai-textanalytics azure-keyvault-secrets azure-identity tiktoken

  
### Setup  
  
1. Clone this repository:  
  
git clone https://github.com/yourusername/ai-collaboration-tool.git
cd ai-collaboration-tool

  
2. Set up the required environment variables:  
  
export GPT_API_ENDPOINT=<Your GPT API endpoint>
export GPT_API_KEY=<Your GPT API key>
export GPT_API_ENDPOINT2=<Your GPT API endpoint for the second AI instance>
export GPT_API_KEY2=<Your GPT API key for the second AI instance>
export AZURE_LANGUAGE_ENDPOINT=<Your Azure Language API endpoint>
export AZURE_LANGUAGE_KEY=<Your Azure Language API key>

  
Replace `<Your GPT API endpoint>`, `<Your GPT API key>`, `<Your GPT API endpoint for the second AI instance>`, `<Your GPT API key for the second AI instance>`, `<Your Azure Language API endpoint>`, and `<Your Azure Language API key>` with the respective values for your API keys and endpoints.  
 
# Code Explanation 
 
This section explains the code in detail. The AI Collaboration Tool works by using two AI instances to solve a user's problem. It generates Python code based on user input, validates the generated code, and ensures the same code is not added multiple times. 
## Importing Libraries 
 
The required libraries are imported at the beginning of the script.
<pre>
import tiktoken  
import openai  
import os  
import time  
from azure.identity import ChainedTokenCredential, DefaultAzureCredential, ManagedIdentityCredential  
from azure.keyvault.secrets import SecretClient  
from azure.ai.textanalytics import TextAnalyticsClient  
from azure.core.credentials import AzureKeyCredential  
import subprocess  
</pre>

## Defining Variables 
 
Global variables for the AI instances, API keys, and API endpoints are defined. 
<pre>
model = "gpt-4-32k"  
openai.api_type = "azure"  
openai.api_version = "2023-03-15-preview"  
AI1_API_BASE = os.getenv("GPT_API_ENDPOINT")  
AI1_API_KEY = os.getenv("GPT_API_KEY")  
AI2_API_BASE = os.getenv("GPT-API-ENDPOINT2")  
AI2_API_KEY = os.getenv("GPT-API-KEY2")  
  
AZURE_LANGUAGE_ENDPOINT = os.getenv("AZURE_LANGUAGE_ENDPOINT")  
AZURE_LANGUAGE_KEY = os.getenv("AZURE_LANGUAGE_KEY")  
</pre>

## AI System Messages 
 
System messages for AI1 and AI2 are defined. These messages instruct the AI instances on their roles and how they should collaborate.
<pre> 
system_message1 = {"role": "system", "content": "You are an AI number 1. ..."}  
system_message2 = {"role": "system", "content": "You are an AI number 2. ..."}  
</pre> 

## Authentication and Key Phrases Extraction 
 
The following functions are used to authenticate the Azure Language Client and extract key phrases from a document: 
<pre>
def authenticate_language_client():  
    # ...  
  
def extract_key_phrases(client, document):  
    # ...  
</pre> 

## Code File Handling 
 
These functions are used to read and append code to the "generated_code.py" file: 
<pre>
def append_code_to_file(code, file_path):  
    # ...  
  
def read_code_from_file(file_path):  
    # ...  
</pre>

## Token Counting 
 
The num_tokens_from_messages function calculates the number of tokens in the conversation history. 
<pre>
def num_tokens_from_messages(messages, model="gpt-3.5-turbo-0301"):  
    # ...  
 </pre>

## AI Responses 
 
The ai1_response and ai2_response functions are used to get responses from the two AI instances. 
<pre>
def ai1_response(conversation, AI1_API_BASE, AI1_API_KEY):  
    # ...  
  
def ai2_response(conversation, AI2_API_BASE, AI2_API_KEY):  
    # ...  
 </pre>

## Code Validation 
 
The validate_code function validates the Python code present in the "generated_code.py" file. 
<pre>
def validate_code(file_path):  
    # ...  
</pre> 

## AI Conversation Loop 
 
The ai_conversation_loop function is responsible for the main conversation loop between the two AI instances. 
<pre>
def ai_conversation_loop(conversation, max_duration=1200, ai1_api_base=None, ai1_api_key=None, ai2_api_base=None, ai2_api_key=None):  
    # ...  
</pre> 

## Main User Interaction Loop 
 
The main loop allows the user to input their problems or requests and runs the AI conversation loop. 
<pre>
while (True):  
    user_input = input("User: ")  
    conversation.append({"role": "user", "content": user_input})  
    conversation = ai_conversation_loop(conversation, ai1_api_base=AI1_API_BASE, ai1_api_key=AI1_API_KEY, ai2_api_base=AI2_API_BASE, ai2_api_key=AI2_API_KEY)  
</pre> 
This is a high-level overview of the code. The AI instances collaborate and generate Python code based on the user's input, and the code is saved in the "generated_code.py" file. The code is validated to ensure it works as intended.

Note that you can also do other stuff with this application than generate code.

---
**NOTE**

I'm not a developer so there probably are lot's of weird things or issues in my code. I'm just testing things out by coding with OpenAI. So don't take it too seriously WHEN you find issues and something to fix in my code :)

---