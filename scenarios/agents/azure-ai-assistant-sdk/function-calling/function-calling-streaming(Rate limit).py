from typing import Dict, Union

from azure.ai.assistants import AssistantsClient
from azure.ai.assistants.models import (
    AssistantEventHandler,
    FunctionTool,
    MessageDeltaChunk,
    MessageDeltaTextContent,
    RunStep,
    ThreadMessage,
    ThreadRun,
    ToolSet,
)
from azure.identity import DefaultAzureCredential
from user_functions import user_functions  # found in the user_functions.py file in this directory.

project_endpoint = "https://acct418a.services.ai.azure.com/api/projects/prj1"
model_deployment_name = "gpt-4o-mini-deployment"  # Change if you deployed a different model

assistants_client = AssistantsClient(
    endpoint=project_endpoint,  # os.environ["PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential(),
)


# When using FunctionTool with ToolSet in agent creation, the tool call events are handled inside the create_stream
# method and functions gets automatically called by default.
class MyEventHandler(AssistantEventHandler):
    def on_message_delta(self, delta: "MessageDeltaChunk") -> None:
        for content_part in delta.delta.content:
            if isinstance(content_part, MessageDeltaTextContent):
                text_value = content_part.text.value if content_part.text else "No text"
                print(f"Text delta received: {text_value}")

    def on_thread_message(self, message: "ThreadMessage") -> None:
        print(f"ThreadMessage created. ID: {message.id}, Status: {message.status}")

    def on_thread_run(self, run: "ThreadRun") -> None:
        print(f"ThreadRun status: {run.status}")

        if run.status == "failed":
            print(f"Run failed. Error: {run.last_error}")

    def on_run_step(self, step: "RunStep") -> None:
        print(f"RunStep type: {step.type}, Status: {step.status}")

    def on_error(self, data: str) -> None:
        print(f"An error occurred. Data: {data}")

    def on_done(self) -> None:
        print("Stream completed.")

    def on_unhandled_event(self, event_type: str, event_data: Union[str, Dict[str, any]]) -> None:
        print(f"Unhandled Event Type: {event_type}, Data: {event_data}")


with assistants_client:
    functions = FunctionTool(user_functions)
    toolset = ToolSet()
    toolset.add(functions)

    assistant = assistants_client.create_assistant(
        model=model_deployment_name, name="my-assistant", instructions="You are a helpful assistant", toolset=toolset
    )
    print(f"Created agent, ID: {assistant.id}")

    thread = assistants_client.create_thread()
    print(f"Created thread, thread ID {thread.id}")

    message = assistants_client.create_message(
        thread_id=thread.id,
        role="user",
        content="Hello, send an email with the datetime and weather information in New York? Also let me know the details",
    )
    print(f"Created message, message ID {message.id}")

    with assistants_client.create_stream(
        thread_id=thread.id, assistant_id=assistant.id, event_handler=MyEventHandler()
    ) as stream:
        stream.until_done()

    assistants_client.delete_assistant(assistant.id)
    print("Deleted agent")

    messages = assistants_client.list_messages(thread_id=thread.id)
    print(f"Messages: {messages}")
