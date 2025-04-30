# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to use basic assistant operations from
    the Azure Assistants service using a synchronous client.

USAGE:
    python sample_assistants_basics.py

    Before running the sample:

    pip install azure-ai-assistants azure-identity

    Set these environment variables with your own values:
    1) PROJECT_ENDPOINT - the Azure AI Assistants endpoint.
    2) MODEL_DEPLOYMENT_NAME - The deployment name of the AI model, as found under the "Name" column in 
    the "Models + endpoints" tab in your Azure AI Foundry project.
"""

import time
from azure.ai.assistants import AssistantsClient
from azure.identity import DefaultAzureCredential
from azure.ai.assistants.models import ListSortOrder, MessageTextContent

# Format of the project_endpoint is https://<your-ai-services-account-name>.services.ai.azure.com/api/projects/<your-project-name>
project_endpoint = "https://acct418a.services.ai.azure.com/api/projects/prj1"
# project_endpoint = "https://shpeng1rpcanary417.services.ai.azure.com/api/projects/basic-nocaphost"  # Canary
# [START create_project_client]
assistants_client = AssistantsClient(
    endpoint=project_endpoint,       #os.environ["PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential(),
)
# [END create_project_client]

model_deployment_name = "gpt-4o-mini-deployment"  # Change if you deployed a different model
with assistants_client:
    # [START create_assistant]
    assistant = assistants_client.create_assistant(
        model=model_deployment_name,                # os.environ["MODEL_DEPLOYMENT_NAME"],
        name="my-assistant",
        instructions="You are a helpful assistant",
    )
    # [END create_assistant]
    print(f"Created assistant, assistant ID: {assistant.id}")

    # [START create_thread]
    thread = assistants_client.create_thread()
    # [END create_thread]
    print(f"Created thread, thread ID: {thread.id}")

    # [START create_message]
    message = assistants_client.create_message(thread_id=thread.id, role="user", content="Hello, tell me a joke")
    # [END create_message]
    print(f"Created message, message ID: {message.id}")

    # [START create_run]
    run = assistants_client.create_run(thread_id=thread.id, assistant_id=assistant.id)

    # Poll the run as long as run status is queued or in progress
    while run.status in ["queued", "in_progress", "requires_action"]:
        # Wait for a second
        time.sleep(1)
        run = assistants_client.get_run(thread_id=thread.id, run_id=run.id)
        # [END create_run]
        print(f"Run status: {run.status}")

    assistants_client.delete_assistant(assistant.id)
    print("Deleted assistant")

    # [START list_messages]
    messages = assistants_client.list_messages(thread_id=thread.id, order=ListSortOrder.ASCENDING)

    # The messages are following in the reverse order,
    # we will iterate them and output only text contents.
    for data_point in messages.data:
        last_message_content = data_point.content[-1]
        if isinstance(last_message_content, MessageTextContent):
            print(f"{data_point.role}: {last_message_content.text.value}")

    # [END list_messages]
