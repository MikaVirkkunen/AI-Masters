import tiktoken
import openai
import os
import time
from azure.identity import ChainedTokenCredential, DefaultAzureCredential, ManagedIdentityCredential
from azure.keyvault.secrets import SecretClient
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential


# model = "gpt-35-turbo-version-0301"
model = "gpt-4-32k"
openai.api_type = "azure"
openai.api_version = "2023-03-15-preview"
AI1_API_BASE = os.getenv("GPT_API_ENDPOINT")
AI1_API_KEY = os.getenv("GPT_API_KEY")
AI2_API_BASE = os.getenv("GPT-API-ENDPOINT2")
AI2_API_KEY = os.getenv("GPT-API-KEY2")

AZURE_LANGUAGE_ENDPOINT = os.getenv("AZURE_LANGUAGE_ENDPOINT")
AZURE_LANGUAGE_KEY = os.getenv("AZURE_LANGUAGE_KEY")

system_message1 = {"role": "system", "content": "You are an AI number 1. You task is to handle user problems together with AI number 2. Plan together how to solve user problem, suggest ideas to each others, validate others ideas, be critical and test and understand if other AI solutions work. Think if there's a better way to do it. Don't give up too early. You need to do what user wants and not quit too soon. If user gives you a task, make sure you do it. If you need to write code validate that it does what user asked it to do. If not. continue developing it. Double check the code at the end that it's correct."}
system_message2 = {"role": "system", "content": "You are an AI number 2. You task is to handle user problems together with AI number 1. Plan together how to solve user problem, suggest ideas to each others, validate others ideas, be critical and test and understand if other AI solutions work. Think if there's a better way to do it. Don't give up too early. You need to do what user wants and not quit too soon. If user gives you a task, make sure you do it. If you need to write code validate that it does what user asked it to do. If not. continue developing it. double check the code at the end that it's correct."}
max_response_tokens = 4000
token_limit = 32000
conversation = []
conversation.append(system_message1)
conversation.append(system_message2)


def authenticate_language_client():
    ta_credential = AzureKeyCredential(AZURE_LANGUAGE_KEY)
    language_client = TextAnalyticsClient(
        endpoint=AZURE_LANGUAGE_ENDPOINT, credential=ta_credential)
    return language_client


def extract_key_phrases(client, document):
    response = client.extract_key_phrases(
        documents=[{"id": "1", "text": document}])[0]
    if not response.is_error:
        return response.key_phrases
    else:
        return []


def save_code_to_file(code, file_path):
    with open(file_path, "w") as f:
        f.write(code)

def num_tokens_from_messages(messages, model="gpt-3.5-turbo-0301"):
    encoding = tiktoken.encoding_for_model(model)
    num_tokens = 0
    for message in messages:
        num_tokens += 4
        for key, value in message.items():
            num_tokens += len(encoding.encode(value))
            if key == "name":
                num_tokens += -1
    num_tokens += 2
    return num_tokens


def ai1_response(conversation, AI1_API_BASE, AI1_API_KEY):
    openai.api_base = AI1_API_BASE
    openai.api_key = AI1_API_KEY
    response = openai.ChatCompletion.create(
        engine=model,
        messages=conversation,
        temperature=.7,
        max_tokens=max_response_tokens,
    )
    if "generate python code" in conversation[-1]["content"].lower():
        key_phrases = extract_key_phrases(
            authenticate_language_client(), conversation[-1]["content"])
        prompt = f"Write a Python script to {', '.join(key_phrases)}"
        response = openai.Completion.create(
            engine="davinci-codex",
            prompt=prompt,
            temperature=0.5,
            max_tokens=200,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
    return response


def ai2_response(conversation, AI2_API_BASE, AI2_API_KEY):
    openai.api_base = AI2_API_BASE
    openai.api_key = AI2_API_KEY
    response = openai.ChatCompletion.create(
        engine=model,
        messages=conversation,
        temperature=.7,
        max_tokens=max_response_tokens,
    )
    if "generate python code" in conversation[-1]["content"].lower():
        key_phrases = extract_key_phrases(
            authenticate_language_client(), conversation[-1]["content"])
        prompt = f"Write a Python script to {', '.join(key_phrases)}"
        response = openai.Completion.create(
            engine="davinci-codex",
            prompt=prompt,
            temperature=0.5,
            max_tokens=200,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
    return response


def ai_conversation_loop(conversation, max_duration=600, ai1_api_base=None, ai1_api_key=None, ai2_api_base=None, ai2_api_key=None):
    start_time = time.time()
    duration = 0

    if conversation[-1]["role"] == "user":
        user_message = conversation[-1]["content"]
        custom_message = f"Hey AI2, user wants us to solve this problem for him: {user_message}. Let's help the user with this problem. What are your initial thoughts?"
        conversation.append({"role": "assistant", "content": custom_message})
        print("\nAI 1: " + custom_message + "\n")

    while duration < max_duration:
        conv_history_tokens = num_tokens_from_messages(conversation)
        while (conv_history_tokens + max_response_tokens >= token_limit):
            del conversation[1]
            conv_history_tokens = num_tokens_from_messages(conversation)

        response1 = ai1_response(conversation, ai1_api_base, ai1_api_key)
        conversation.append(
            {"role": "assistant", "content": response1['choices'][0]['message']['content']})
        print("\nAI 1: " + response1['choices']
              [0]['message']['content'] + "\n")

        conv_history_tokens = num_tokens_from_messages(conversation)
        while (conv_history_tokens + max_response_tokens >= token_limit):
            del conversation[1]
            conv_history_tokens = num_tokens_from_messages(conversation)

        response2 = ai2_response(conversation, ai2_api_base, ai2_api_key)
        conversation.append(
            {"role": "assistant", "content": response2['choices'][0]['message']['content']})
        print("\nAI 2: " + response2['choices']
              [0]['message']['content'] + "\n")

        duration = time.time() - start_time

        # Check if both AI instances have generated Python code
        if "```python" in response1['choices'][0]['message']['content'] and "```python" in response2['choices'][0]['message']['content']:
            code1 = response1['choices'][0]['message']['content'].split("```python")[
                1].split("```")[0].strip()
            code2 = response2['choices'][0]['message']['content'].split("```python")[
                1].split("```")[0].strip()

            # Combine the code from both AIs
            combined_code = f"{code1}\n\n{code2}"

            # Save the combined code to a file
            save_code_to_file(combined_code, "generated_code.py")
            print("\nThe generated Python code has been saved to 'generated_code.py'.\n")

        if "ready" in response1['choices'][0]['message']['content'].lower() and "ready" in response2['choices'][0]['message']['content'].lower():
            break

    return conversation



while (True):
    user_input = input("User: ")
    conversation.append({"role": "user", "content": user_input})
    conversation = ai_conversation_loop(conversation, ai1_api_base=AI1_API_BASE, ai1_api_key=AI1_API_KEY, ai2_api_base=AI2_API_BASE, ai2_api_key=AI2_API_KEY)
