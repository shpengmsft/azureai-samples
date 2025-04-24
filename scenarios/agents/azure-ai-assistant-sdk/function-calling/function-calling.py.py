import time

from azure.ai.assistants import AssistantsClient
from azure.ai.assistants.models import FunctionTool, RequiredFunctionToolCall, SubmitToolOutputsAction
from azure.identity import DefaultAzureCredential
from user_functions import user_functions  # found in the user_functions.py file in this directory.

project_endpoint = "https://acct418a.services.ai.azure.com/api/projects/prj1"
model_deployment_name = "gpt-4o-mini-deployment"  # Change if you deployed a different model

assistants_client = AssistantsClient(
    endpoint=project_endpoint,  # os.environ["PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential(),
)

# Initialize function tool with user functions
functions = FunctionTool(functions=user_functions)

with assistants_client:
    # [START create_assistant]
    assistant = assistants_client.create_assistant(
        model=model_deployment_name,  # os.environ["MODEL_DEPLOYMENT_NAME"],
        name="my-assistant",
        instructions="You are a helpful assistant",
        tools=functions.definitions,
    )
    # [END create_assistant]
    print(f"Created assistant, assistant ID: {assistant.id}")

    thread = assistants_client.create_thread()
    print(f"Created thread, ID: {thread.id}")

    # [START create_message]
    message = assistants_client.create_message(
        thread_id=thread.id,
        role="user",
        content="Hello, Please send an email with the datetime and weather information in New York.",
    )
    # [END create_message]
    print(f"Created message, message ID: {message.id}")

    run = assistants_client.create_run(thread_id=thread.id, assistant_id=assistant.id)
    print(f"Created run, ID: {run.id}")

    while run.status in ["queued", "in_progress", "requires_action"]:
        time.sleep(1)
        run = assistants_client.get_run(thread_id=thread.id, run_id=run.id)

        if run.status == "requires_action" and isinstance(run.required_action, SubmitToolOutputsAction):
            tool_calls = run.required_action.submit_tool_outputs.tool_calls
            if not tool_calls:
                print("No tool calls provided - cancelling run")
                assistants_client.cancel_run(thread_id=thread.id, run_id=run.id)
                break

            tool_outputs = []
            for tool_call in tool_calls:
                if isinstance(tool_call, RequiredFunctionToolCall):
                    try:
                        output = functions.execute(tool_call)
                        print(f"Tool call {tool_call.id} executed successfully with Output: {output}")
                        tool_outputs.append(
                            {
                                "tool_call_id": tool_call.id,
                                "output": output,
                            }
                        )
                    except Exception as e:
                        print(f"Error executing tool_call {tool_call.id}: {e}")

            print(f"Tool outputs: {tool_outputs}")
            if tool_outputs:
                assistants_client.submit_tool_outputs_to_run(
                    thread_id=thread.id, run_id=run.id, tool_outputs=tool_outputs
                )

        print(f"Current run status: {run.status}")

    print(f"Run completed with status: {run.status}")

    # Delete the agent when done
    assistants_client.delete_assistant(assistant.id)
    print("Deleted agent")

    # Fetch and log all messages
    messages = assistants_client.list_messages(thread_id=thread.id)
    print(f"Messages: {messages}")
