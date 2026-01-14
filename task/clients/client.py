from aidial_client import Dial, AsyncDial

from task.clients.base import BaseClient
from task.constants import DIAL_ENDPOINT
from task.models.message import Message
from task.models.role import Role


class DialClient(BaseClient):

    def __init__(self, deployment_name: str):
        super().__init__(deployment_name)

        self.dial_client = Dial(
            api_key=self._api_key,
            base_url=DIAL_ENDPOINT
        )
        self.async_dial_client = AsyncDial(
            api_key=self._api_key,
            base_url=DIAL_ENDPOINT
        )


    def get_completion(self, messages: list[Message]) -> Message:
        completion = self.dial_client.chat.completions.create(
            deployment_name=self._deployment_name,
            messages=[msg.to_dict() for msg in messages],
            stream=False,
        )
        try:
            choices = completion.choices
        except:
            raise Exception("No choices in response found")
        
        try:
            message = choices[0].message
        except:
            raise Exception("No message in choices found")
        
        try:
            content = message.content
        except:
            raise Exception("No content in message found")
        
        print(content)
        return Message(
            role=Role.AI,
            content=content
        )
    

    async def stream_completion(self, messages: list[Message]) -> Message:
        completion = await self.async_dial_client.chat.completions.create(
            deployment_name=self._deployment_name,
            messages=[msg.to_dict() for msg in messages],
            stream=True,
        )
        contents = []
        async for chunk in completion:
            try:
                choices = chunk.choices
            except:
                raise Exception("No choices in chunk found")
            
            try:
                delta = choices[0].delta
            except:
                raise Exception("No delta in choices found")
            
            try:
                content = delta.content
            except:
                raise Exception("No content in delta found")
            
            if content:
                print(content)
                contents.append(content)

        print()
        return Message(
            role=Role.AI,
            content=' '.join(contents)
        )

