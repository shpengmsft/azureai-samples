# This sample demonstrates how to use agent operations with toolset from the Azure Agents service using a synchronous client. It's purpose is to showcase automatic tool calling using ToolSet in non-streaming scenario

import os

from azure.ai.assistants import AssistantsClient
from azure.ai.assistants.models import CodeInterpreterTool, FunctionTool, ToolSet
from azure.identity import DefaultAzureCredential
from user_functions import user_functions  # found in the user_functions.py file in this directory.

project_endpoint = "https://acct418a.services.ai.azure.com/api/projects/prj1"
model_deployment_name = "gpt-4o-mini-deployment"  # Change if you deployed a different model

assistants_client = AssistantsClient(
    endpoint=project_endpoint,  # os.environ["PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential(),
)

# Initialize agent toolset with user functions and code interpreter
functions = FunctionTool(user_functions)
code_interpreter = CodeInterpreterTool()

toolset = ToolSet()
toolset.add(functions)
toolset.add(code_interpreter)

# Create agent with toolset and process assistant run
with assistants_client:
    assistant = assistants_client.create_assistant(
        model=model_deployment_name, name="my-assistant", instructions="You are a helpful assistant", toolset=toolset
    )
    print(f"Created assistant, ID: {assistant.id}")

    # Create thread for communication
    thread = assistants_client.create_thread()
    print(f"Created thread, ID: {thread.id}")

    # Create message to thread
    message = assistants_client.create_message(
        thread_id=thread.id,
        role="user",
        content="Hello, send an email with the datetime and weather information in New York?",
    )
    print(f"Created message, ID: {message.id}")

    # Create and process agent run in thread with tools
    run = assistants_client.create_and_process_run(thread_id=thread.id, assistant_id=assistant.id)
    print(f"Run finished with status: {run.status}")

    if run.status == "failed":
        print(f"Run failed: {run.last_error}")

    # Delete the assistant when done
    assistants_client.delete_agent(assistant.id)
    print("Deleted agent")

    # Fetch and log all messages
    messages = assistants_client.list_messages(thread_id=thread.id)
    print(f"Messages: {messages}")
