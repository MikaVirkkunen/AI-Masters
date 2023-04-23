import tiktoken
import openai
import os
import time
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential
import subprocess
from googlesearch import search

model = "gpt-35-turbo-version-0301"
# model = "gpt-4-32k"
openai.api_type = "azure"
openai.api_version = "2023-03-15-preview"
AI1_API_BASE = os.getenv("GPT_API_ENDPOINT")
AI1_API_KEY = os.getenv("GPT_API_KEY")
AI2_API_BASE = os.getenv("GPT-API-ENDPOINT2")
AI2_API_KEY = os.getenv("GPT-API-KEY2")

AZURE_LANGUAGE_ENDPOINT = os.getenv("AZURE_LANGUAGE_ENDPOINT")
AZURE_LANGUAGE_KEY = os.getenv("AZURE_LANGUAGE_KEY")

system_message1 = {"role": "system", "content": "You are AI 1. Remember, you are AI 1 and not AI 2. Your task is to handle user problems together with AI 2. Always address each other as AI 1 and AI 2. Plan together how to solve user problem, suggest ideas to each other, validate each other's ideas, be critical and test and understand if other AI solutions work. Think if there's a better way to do it. Don't give up too early. You need to do what user wants and not quit too soon. If user gives you a task, make sure you do it. You can also search answers from the internet by using the words: search the web for. Always wait until other AI has responsed so don't response two times in a row."}
system_message2 = {"role": "system", "content": "You are AI 2. Remember, you are AI 2 and not AI 1. Your task is to handle user problems together with AI 1. Always address each other as AI 2 and AI 1. Plan together how to solve user problem, suggest ideas to each other, validate each other's ideas, be critical and test and understand if other AI solutions work. Think if there's a better way to do it. Don't give up too early. You need to do what user wants and not quit too soon. If user gives you a task, make sure you do it. You can also search answers from the internet by using the words: search the web for. Always wait until other AI has responsed so don't response two times in a row."}

max_response_tokens = 4000
token_limit = 32000
conversation = []
conversation.append(system_message1)
conversation.append(system_message2)


def perform_web_search(query, num_results=5):
    search_results = []
    try:
        for result in search(query, num_results=num_results):
            search_results.append(result)
    except Exception as e:
        print(f"Error while performing web search: {e}")
    return search_results


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


def append_code_to_file(code, file_path):
    with open(file_path, "a") as f:
        f.write(code + "\n")


def read_code_from_file(file_path):
    with open(file_path, "r") as f:
        return f.read()


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
        temperature=0.5,
        max_tokens=max_response_tokens,
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
    return response


def extract_code(response_content):
    if "```python" in response_content:
        code = response_content.split("```python")[1].split("```")[0].strip()
        return code
    return None


def validate_code(file_path):
    try:
        subprocess.check_output(["python", file_path])
        print("\nThe code in the 'generated_code.py' file is valid.\n")
    except subprocess.CalledProcessError as e:
        print("\nThe code in the 'generated_code.py' file is not valid.\n")


def request_more_info(conversation):
    conversation.append(
        {"role": "assistant", "name": "AI_1", "content": "We need more information or clarification on this topic. Can you please provide more details?"})
    print("\nAI 1: We need more information or clarification on this topic. Can you please provide more details?\n")


def ai_conversation_loop(conversation, max_duration=1200, ai1_api_base=None, ai1_api_key=None, ai2_api_base=None, ai2_api_key=None):
    start_time = time.time()
    duration = 0
    code_generated = False

    with open("generated_code.py", "w") as f:
        f.write("")

    if conversation[-1]["role"] == "user":
        user_message = conversation[-1]["content"]
        custom_message = f"Hey AI_2, user wants us to solve this problem for him: {user_message}. Let's help the user with this problem. What are your initial thoughts?"
        conversation.append(
            {"role": "assistant", "name": "AI_1", "content": custom_message})
        print("\nAI 1: " + custom_message + "\n")

    while duration < max_duration:
        conv_history_tokens = num_tokens_from_messages(conversation)
        while (conv_history_tokens + max_response_tokens >= token_limit):
            del conversation[1]
            conv_history_tokens = num_tokens_from_messages(conversation)

        response1 = ai1_response(conversation, ai1_api_base, ai1_api_key)
        conversation.append(
            {"role": "assistant", "name": "AI_1", "content": response1['choices'][0]['message']['content']})
        print("\nAI 1: " + response1['choices']
              [0]['message']['content'] + "\n")

        if "need more information" in response1['choices'][0]['message']['content'].lower():
            request_more_info(conversation)
            continue

        conv_history_tokens = num_tokens_from_messages(conversation)
        while (conv_history_tokens + max_response_tokens >= token_limit):
            del conversation[1]
            conv_history_tokens = num_tokens_from_messages(conversation)

        response2 = ai2_response(conversation, ai2_api_base, ai2_api_key)
        conversation.append(
            {"role": "assistant", "name": "AI_2", "content": response2['choices'][0]['message']['content']})
        print("\nAI 2: " + response2['choices']
              [0]['message']['content'] + "\n")

        if "need more information" in response2['choices'][0]['message']['content'].lower():
            request_more_info(conversation)
            continue

        search_query = None
        if "search the web for" in response1['choices'][0]['message']['content'].lower():
            search_query = response1['choices'][0]['message']['content'].split(
                "search the web for ")[1].split(".")[0]
        elif "search the web for" in response2['choices'][0]['message']['content'].lower():
            search_query = response2['choices'][0]['message']['content'].split(
                "search the web for ")[1].split(".")[0]

        if search_query:
            search_results = perform_web_search(search_query)
            search_results_str = "\n".join(search_results)
            conversation.append({"role": "assistant", "name": "AI_1",
                                "content": f"I found the following results for your search query '{search_query}':\n{search_results_str}"})
            print(
                f"\nAI 1: I found the following results for your search query '{search_query}':\n{search_results_str}\n")

        duration = time.time() - start_time
        code1 = None
        code2 = None
        if "```python" in response1['choices'][0]['message']['content']:
            code1 = extract_code(response1['choices'][0]['message']['content'])
        if code1:
            existing_code = read_code_from_file("generated_code.py")
            if code1 not in existing_code:
                append_code_to_file(code1, "generated_code.py")
                code_generated = True

        code2 = extract_code(response2['choices'][0]['message']['content'])
        if code2:
            existing_code = read_code_from_file("generated_code.py")
            if code2 not in existing_code:
                append_code_to_file(code2, "generated_code.py")
                code_generated = True

        if code_generated and "ready" in response1['choices'][0]['message']['content'].lower() and "ready" in response2['choices'][0]['message']['content'].lower():
            validate_code("generated_code.py")
            break

    return conversation, search_query


while (True):
    user_input = input("User: ")
    conversation.append({"role": "user", "content": user_input})

    search_query = None
    if "search the web for" in user_input.lower():
        search_query = user_input.split("search the web for ")[1].split(".")[0]

    if search_query:
        search_results = perform_web_search(search_query)
        search_results_str = "\n".join(search_results)
        conversation.append({"role": "assistant", "name": "AI_1",
                            "content": f"I found the following results for your search query '{search_query}':\n{search_results_str}"})
        print(
            f"\nAI 1: I found the following results for your search query '{search_query}':\n{search_results_str}\n")

    conversation, search_query = ai_conversation_loop(
        conversation, ai1_api_base=AI1_API_BASE, ai1_api_key=AI1_API_KEY, ai2_api_base=AI2_API_BASE, ai2_api_key=AI2_API_KEY)

    if search_query:
        search_results = perform_web_search(search_query)
        search_results_str = "\n".join(search_results)
        conversation.append({"role": "assistant", "name": "AI_1",
                            "content": f"I found the following results for your search query '{search_query}':\n{search_results_str}"})
        print(
            f"\nAI 1: I found the following results for your search query '{search_query}':\n{search_results_str}\n")
