import tiktoken
import openai
import os
import time
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential
import subprocess
from googlesearch import search
import re

# Set model and API information
# model = "gpt-35-turbo-version-0301"
model = "gpt-4-32k"
openai.api_type = "azure"
openai.api_version = "2023-03-15-preview"
AI1_API_BASE = os.getenv("GPT_API_ENDPOINT")
AI1_API_KEY = os.getenv("GPT_API_KEY")
AI2_API_BASE = os.getenv("GPT_API_ENDPOINT2")
AI2_API_KEY = os.getenv("GPT_API_KEY2")

AZURE_LANGUAGE_ENDPOINT = os.getenv("AZURE_LANGUAGE_ENDPOINT")
AZURE_LANGUAGE_KEY = os.getenv("AZURE_LANGUAGE_KEY")

system_message1 = {"role": "system", "content": "You are AI 1. Remember, you are AI 1 and not AI 2. Your task is to handle user problems together with AI 2. Always address each other as AI 1 and AI 2. Plan together how to solve user problem, suggest ideas to each other, validate each other's ideas, be critical and test and understand if other AI solutions work. Think if there's a better way to do it. Don't give up too early. You need to do what user wants and not quit too soon. If user gives you a task, make sure you do it. You can also search answers from the internet by using the words: search the web for. Always wait until other AI has responsed so don't response two times in a row."}
system_message2 = {"role": "system", "content": "You are AI 2. Remember, you are AI 2 and not AI 1. Your task is to handle user problems together with AI 1. Always address each other as AI 2 and AI 1. Plan together how to solve user problem, suggest ideas to each other, validate each other's ideas, be critical and test and understand if other AI solutions work. Think if there's a better way to do it. Don't give up too early. You need to do what user wants and not quit too soon. If user gives you a task, make sure you do it. You can also search answers from the internet by using the words: search the web for. Always wait until other AI has responsed so don't response two times in a row."}

max_response_tokens = 4000
token_limit = 32000
conversation = []
conversation.append(system_message1)
conversation.append(system_message2)

# Function to analyze content and suggest changes


def analyze_and_suggest_changes(file_paths, conversation):
    file_contents = []
    for file_path in file_paths:
        with open(file_path, "r") as f:
            file_contents.append(f.read())

    file_content_str = "\n\n".join(file_contents)
    conversation.append(
        {"role": "user", "content": f"Analyze the following content and suggest changes: {file_content_str}"})

    conversation, _ = ai_conversation_loop(
        conversation, ai1_api_base=AI1_API_BASE, ai1_api_key=AI1_API_KEY, ai2_api_base=AI2_API_BASE, ai2_api_key=AI2_API_KEY)

    suggestions = []
    for message in conversation:
        if message["role"] == "assistant" and "suggestion:" in message["content"].lower():
            suggestion = message["content"].split("Suggestion:")[1].strip()
            suggestions.append(suggestion)

    return suggestions

# Function to write suggestions to a file


def write_suggestions_to_file(suggestions, output_file):
    with open(output_file, "w") as f:
        for suggestion in suggestions:
            f.write(suggestion + "\n")

# Function to perform a web search


def perform_web_search(query, num_results=5):
    search_results = []
    try:
        for result in search(query, num_results=num_results):
            search_results.append(result)
    except Exception as e:
        print(f"Error while performing web search: {e}")
    return search_results

# Function to authenticate the Azure language client


def authenticate_language_client():
    ta_credential = AzureKeyCredential(AZURE_LANGUAGE_KEY)
    language_client = TextAnalyticsClient(
        endpoint=AZURE_LANGUAGE_ENDPOINT, credential=ta_credential)
    return language_client

# Function to extract key phrases from a document


def extract_key_phrases(client, document):
    response = client.extract_key_phrases(
        documents=[{"id": "1", "text": document}])[0]
    if not response.is_error:
        return response.key_phrases
    else:
        return []

# Function to append code to a file


def append_code_to_file(code, file_path):
    with open(file_path, "a") as f:
        f.write(code + "\n")

# Function to read code from a file


def read_code_from_file(file_path):
    with open(file_path, "r") as f:
        return f.read()

# Function to calculate the number of tokens in messages


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

# Function to perform a conversation loop between two AIs


def ai_response(conversation, role, ai1_api_base, ai1_api_key, ai2_api_base, ai2_api_key):
    if role == "AI_1":
        openai.api_base = ai1_api_base
        openai.api_key = ai1_api_key
    elif role == "AI_2":
        openai.api_base = ai2_api_base
        openai.api_key = ai2_api_key
    else:
        raise ValueError("Invalid role. Role should be 'AI_1' or 'AI_2'.")

    response = openai.ChatCompletion.create(
        engine=model,
        messages=conversation,
        temperature=0.5,
        max_tokens=max_response_tokens,
    )

    response_content = response['choices'][0]['message']['content']

    return response_content

# Function to extract Python code from a response content string


def extract_code(response_content):
    if "```python" in response_content:
        code = response_content.split("```python")[1].split("```")[0].strip()
        return code
    return None

# Function to validate code.


def validate_code(file_path):
    try:
        subprocess.check_output(["python", file_path])
        print("\nThe code in the 'generated_code.py' file is valid.\n")
    except subprocess.CalledProcessError as e:
        print("\nThe code in the 'generated_code.py' file is not valid.\n")

# Function to request more information from the user


def request_more_info(conversation):
    conversation.append(
        {"role": "assistant", "content": "We need more information or clarification on this topic. Can you please provide more details?"})
    print("\nWe need more information or clarification on this topic. Can you please provide more details?\n")

# Function to save code to a file


def save_code_to_file(code, file_path):
    try:
        with open(file_path, "w") as f:
            f.write(code)
    except Exception as e:
        print(f"Error saving code to file: {e}")

# Function to generate a conversation between AI_1 and AI_2


def ai_conversation_loop(conversation, max_duration=600, ai1_api_base=None, ai1_api_key=None, ai2_api_base=None, ai2_api_key=None):
    start_time = time.time()
    duration = 0
    search_query = None

    if conversation[-1]["role"] == "user":
        user_message = conversation[-1]["content"]
        custom_message = f"User wants us to solve this problem for him: {user_message}. Let's help the user with this problem. What are your initial thoughts?"
        conversation.append(
            {"role": "assistant", "content": custom_message})
        print("\n" + custom_message + "\n")

    while duration < max_duration:
        conv_history_tokens = num_tokens_from_messages(conversation)
        while (conv_history_tokens + max_response_tokens >= token_limit):
            del conversation[1]
            conv_history_tokens = num_tokens_from_messages(conversation)

        response1_content = ai_response(
            conversation, "AI_1", ai1_api_base, ai1_api_key, ai2_api_base, ai2_api_key)
        conversation.append(
            {"role": "assistant", "content": response1_content})
        print("\n" + response1_content + "\n")

        conv_history_tokens = num_tokens_from_messages(conversation)
        while (conv_history_tokens + max_response_tokens >= token_limit):
            del conversation[1]
            conv_history_tokens = num_tokens_from_messages(conversation)

        response2_content = ai_response(
            conversation, "AI_2", ai1_api_base, ai1_api_key, ai2_api_base, ai2_api_key)
        conversation.append(
            {"role": "assistant", "content": response2_content})
        print("\n" + response2_content + "\n")

        duration = time.time() - start_time

        # Check if both AI instances have generated Python code
        code1 = extract_code(response1_content)
        code2 = extract_code(response2_content)

        if code1:
            append_code_to_file(code1, "generated_code.py")
        if code2:
            append_code_to_file(code2, "generated_code.py")

        if "ready" in response1_content.lower() and "ready" in response2_content.lower():
            break

    return conversation, search_query


# Function to append code to a file
while (True):
    user_input = input("User: ")
    user_instruction = "AI 1 and AI 2, please discuss the following topic without quoting each other's messages: "
    user_input_with_instruction = user_instruction + user_input
    conversation.append({"role": "user", "content": user_input})

    search_query = None
    if "search the web for" in user_input.lower():
        search_query = user_input.split("search the web for ")[1].split(".")[0]

    if search_query:
        search_results = perform_web_search(search_query)
        search_results_str = "\n".join(search_results)
        conversation.append({"role": "assistant",
                            "content": f"I found the following results for your search query '{search_query}':\n{search_results_str}"})
        print(
            f"\nI found the following results for your search query '{search_query}':\n{search_results_str}\n")

    # Add the if "analyze" condition here
    if "analyze" in user_input.lower() and "suggest changes" in user_input.lower():
        file_paths = re.findall(r'\b[\w-]+\.\w+', user_input)
        suggestions = analyze_and_suggest_changes(file_paths, conversation)
        write_suggestions_to_file(suggestions, "suggestions.txt")
        print("Suggestions have been written to 'suggestions.txt'")

    conversation, search_query = ai_conversation_loop(
        conversation, ai1_api_base=AI1_API_BASE, ai1_api_key=AI1_API_KEY, ai2_api_base=AI2_API_BASE, ai2_api_key=AI2_API_KEY)

    if search_query:
        search_results = perform_web_search(search_query)
        search_results_str = "\n".join(search_results)
        conversation.append({"role": "assistant",
                            "content": f"I found the following results for your search query '{search_query}':\n{search_results_str}"})
        print(
            f"\nI found the following results for your search query '{search_query}':\n{search_results_str}\n")
