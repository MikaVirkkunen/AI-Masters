import tiktoken
import openai
import os
import time
from azure.identity import ChainedTokenCredential, DefaultAzureCredential, ManagedIdentityCredential
from azure.keyvault.secrets import SecretClient

model = "gpt-35-turbo-version-0301"
openai.api_type = "azure"
openai.api_version = "2023-03-15-preview"
AI1_API_BASE = os.getenv("GPT_API_ENDPOINT")
AI1_API_KEY = os.getenv("GPT_API_KEY")
AI2_API_BASE = os.getenv("GPT-API-ENDPOINT2")
AI2_API_KEY = os.getenv("GPT-API-KEY2")

system_message1 = {"role": "system", "content": "You are an AI number 1. You task is to handle user problems together with AI number 2. Plan together how to solve user problem, suggest ideas to each others, validate others ideas, be critical and test and understand if other AI solutions work. Think if there's a better way to do it."}
system_message2 = {"role": "system", "content": "You are an AI number 2. You task is to handle user problems together with AI number 1. Plan together how to solve user problem, suggest ideas to each others, validate others ideas, be critical and test and understand if other AI solutions work. Think if there's a better way to do it."}
max_response_tokens = 250
token_limit = 4096
conversation = []
conversation.append(system_message1)
conversation.append(system_message2)


def num_tokens_from_messages(messages, model="gpt-3.5-turbo-0301"):
    encoding = tiktoken.encoding_for_model(model)
    num_tokens = 0
    for message in messages:
        # every message follows <im_start>{role/name}\n{content}<im_end>\n
        num_tokens += 4
        for key, value in message.items():
            num_tokens += len(encoding.encode(value))
            if key == "name":  # if there's a name, the role is omitted
                num_tokens += -1  # role is always required and always 1 token
    num_tokens += 2  # every reply is primed with <im_start>assistant
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


def ai_conversation_loop(conversation, max_duration=600, ai1_api_base=None, ai1_api_key=None, ai2_api_base=None, ai2_api_key=None):
    start_time = time.time()
    duration = 0

    # Check if there's a new user message in the conversation
    if conversation[-1]["role"] == "user":
        user_message = conversation[-1]["content"]
        custom_message = f"Hey AI2, user wants us to solve this problem for him: {user_message}. Let's help the user with this problem. What are your initial thoughts?"
        conversation.append({"role": "assistant", "content": custom_message})
        print("\nAI 1: " + custom_message + "\n")

    while duration < max_duration:
        # AI 1
        conv_history_tokens = num_tokens_from_messages(conversation)
        while (conv_history_tokens + max_response_tokens >= token_limit):
            del conversation[1]
            conv_history_tokens = num_tokens_from_messages(conversation)

        response1 = ai1_response(conversation, ai1_api_base, ai1_api_key)
        conversation.append(
            {"role": "assistant", "content": response1['choices'][0]['message']['content']})
        print("\nAI 1: " + response1['choices']
              [0]['message']['content'] + "\n")

        # AI 2
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

        # Check if both AI instances are ready
        if "ready" in response1['choices'][0]['message']['content'].lower() and "ready" in response2['choices'][0]['message']['content'].lower():
            break

    return conversation


while (True):
    user_input = input("User: ")
    conversation.append({"role": "user", "content": user_input})
    conversation = ai_conversation_loop(conversation, ai1_api_base=AI1_API_BASE,
                                        ai1_api_key=AI1_API_KEY, ai2_api_base=AI2_API_BASE, ai2_api_key=AI2_API_KEY)
