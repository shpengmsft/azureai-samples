from azure.ai.assistants.models import MessageRole, BingGroundingTool

bing_tool = BingGroundingTool(connection_id="/subscriptions/bfd9f30e-252d-4fc8-823c-f27d994fc8b7/resourceGroups/balapv-reponses-rg/providers/Microsoft.Bing/accounts/balapv-bing-grounding-responses",)

bing_grounded_assistant = assistants_client.create_assistant(
    model=model,
    name="my-bing-grounded-assistant",
    instructions="You are a helpful assistant that can search the web for information. You can use the Bing search engine to find answers to questions. You should always provide a source for the information you provide.",
    tools=bing_tool.definitions,
    headers={"x-ms-enable-preview": "true"}
)

print(f"Created assistant, assistant ID: {bing_grounded_assistant.id}")

# Create thread for communication
bing_thread = assistants_client.create_thread()
print(f"Created thread, ID: {bing_thread.id}")

# Create message to thread
bing_message = assistants_client.create_message(
    thread_id=bing_thread.id,
    role="user",
    content="What is the top news today",
)
print(f"Created message, ID: {bing_message.id}")

bing_run = assistants_client.create_and_process_run(thread_id=bing_thread.id, assistant_id=bing_grounded_assistant.id)