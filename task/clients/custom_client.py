import json
import aiohttp
import requests

from task.clients.base import BaseClient
from task.constants import DIAL_ENDPOINT
from task.models.message import Message
from task.models.role import Role


class DialClient(BaseClient):
    def __init__(self, deployment_name: str):
        super().__init__(deployment_name)
        self._endpoint = DIAL_ENDPOINT + f"/openai/deployments/{deployment_name}/chat/completions"

    def get_completion(self, messages: list[Message]) -> Message:
        headers = {
            'Api-Key': self._api_key,
            'Content-Type': 'application/json',
        }
        request_data = {
            "model": self._deployment_name,
            "messages": [msg.to_dict() for msg in messages],
            "stream": False
        }
        response = requests.post(
            url=self._endpoint,
            headers=headers,
            json=request_data,
        )
        if response.status_code != 200:
            raise Exception(f"HTTP {response.status_code}: {response.text}")
        
        completion = response.json()

        try:
            choices = completion['choices']
        except:
            raise Exception("No choices in response found")
        
        try:
            message = choices[0]['message']
        except:
            raise Exception("No message in choices found")
        
        try:
            content = message['content']
        except:
            raise Exception("No content in message found")
        
        print(content)
        return Message(
            role=Role.AI,
            content=content
        )

    async def stream_completion(self, messages: list[Message]) -> Message:
        headers = {
            'Api-Key': self._api_key,
            'Content-Type': 'application/json',
        }
        request_data = {
            "model": self._deployment_name,
            "messages": [msg.to_dict() for msg in messages],
            "stream": True
        }

        contents = []
        async with aiohttp.ClientSession() as session:
            async with session.post(url=self._endpoint, headers=headers, json=request_data) as response:
                if response.status == 200:
                    async for line in response.content:
                        line_str = line.decode('utf-8').strip()
                        if line_str.startswith("data: "):
                            data = line_str[6:].strip()
                            if data != "[DONE]":
                                content_snippet = self._get_content_snippet(data)
                                print(content_snippet, end='')
                                contents.append(content_snippet)
                            else:
                                print()
                else:
                    error_text = await response.text()
                    print(f"{response.status} {error_text}")
                return Message(role=Role.AI, content=''.join(contents))

    def _get_content_snippet(self, data: str) -> str:
        """
        Extract content from streaming data chunk.
        """
        data = json.loads(data)
        if choices := data.get("choices"):
            delta = choices[0].get("delta", {})
            return delta.get("content", '')
        return ''
