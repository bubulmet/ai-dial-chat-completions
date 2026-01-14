import asyncio

# from task.clients.client import DialClient
from task.clients.custom_client import DialClient

from task.constants import DEFAULT_SYSTEM_PROMPT
from task.models.conversation import Conversation
from task.models.message import Message
from task.models.role import Role


async def start(stream: bool) -> None:
    dial_client = DialClient(
        deployment_name="gpt-4"
    )

    conversation = Conversation()
    system_prompt = input('System prompt: ')
    if system_prompt == '':
        system_prompt = DEFAULT_SYSTEM_PROMPT
    conversation.add_message(Message(
        role=Role.SYSTEM,
        content=system_prompt
    ))
    while True:
        message_content = input('Your message (`exit` to exit): ')
        if message_content == 'exit':
            break
        conversation.add_message(Message(
            role=Role.USER,
            content=message_content
        ))
        if stream:
            answer = await dial_client.stream_completion(
                messages=conversation.get_messages()
            )
        else:
            answer = dial_client.get_completion(
                messages=conversation.get_messages()
            )

        conversation.add_message(answer)


asyncio.run(
    start(stream=True)
    # start(stream=False)
)
