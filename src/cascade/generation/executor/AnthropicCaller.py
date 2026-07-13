import json
import os
import time

from cascade.generation.executor.LLMCaller import LLMCaller, LLMResponse


class AnthropicCaller(LLMCaller):
    """
        Adapter for Anthropic Claude via the Anthropic Messages API.

        It maps CASCADE's OpenAI-style message and tool format to Anthropic's
        format and maps responses back to the OpenAI-style shape used by the
        existing generators.
    """
    def __init__(
        self,
        max_attempts=1,
        max_tokens=16000,
        temperature=0,
        delay=5,
        dummy=False,
        model="claude-sonnet-4-20250514",
        freq_penalty=0.0,
        api_key=None,
        api_key_env="ANTHROPIC_API_KEY",
        timeout=60.0,
        **kwargs,
    ):
        self.max_attempts = max_attempts
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.delay = delay
        self.model = model
        self.freq_penalty = freq_penalty
        self.dummy = dummy

        if dummy:
            self.client = None
            return

        try:
            from anthropic import Anthropic
        except ImportError as exc:
            raise ImportError(
                "The Anthropic adapter requires the optional 'anthropic' package. "
                "Install it with: pip install anthropic"
            ) from exc

        resolved_api_key_env = api_key_env or "ANTHROPIC_API_KEY"
        self.client = Anthropic(api_key=os.environ.get(resolved_api_key_env, api_key), timeout=timeout)

    def execute(self, prompt, **kwargs):
        if self.dummy:
            return LLMResponse({
                "choices": [{
                    "message": {"role": "assistant", "content": ""},
                    "finish_reason": "stop",
                }]
            })

        tools = kwargs.pop("tools", None)
        attempt = 0
        while attempt < self.max_attempts:
            try:
                system_prompt, messages = self._convert_messages(prompt)
                request_kwargs = {
                    "model": self.model,
                    "max_tokens": self.max_tokens,
                    "temperature": self.temperature,
                    "messages": messages,
                    **kwargs,
                }
                if system_prompt:
                    request_kwargs["system"] = system_prompt
                if tools:
                    request_kwargs["tools"] = self._convert_tools(tools)

                response = self.client.messages.create(**request_kwargs)
                return LLMResponse(self._to_openai_response(response))

            except Exception as e:
                print(f"Generation attempt {attempt + 1} failed: {e}")
                attempt += 1
                time.sleep(self.delay)

        raise Exception("Generation failed because of repeated errors.")

    def _convert_messages(self, prompt):
        system_messages = []
        messages = []

        for message in prompt:
            role = message.get("role")
            content = message.get("content", "")

            if role == "system":
                system_messages.append(content)
                continue

            if role == "assistant":
                converted_content = []
                if content:
                    converted_content.append({"type": "text", "text": content})
                for tool_call in message.get("tool_calls", []) or []:
                    function = tool_call["function"]
                    converted_content.append({
                        "type": "tool_use",
                        "id": tool_call["id"],
                        "name": function["name"],
                        "input": json.loads(function.get("arguments") or "{}"),
                    })
                messages.append({"role": "assistant", "content": converted_content or ""})
                continue

            if role == "tool":
                messages.append({
                    "role": "user",
                    "content": [{
                        "type": "tool_result",
                        "tool_use_id": message["tool_call_id"],
                        "content": content,
                    }]
                })
                continue

            messages.append({"role": "user", "content": content})

        return "\n\n".join(system_messages), messages

    def _convert_tools(self, tools):
        converted = []
        for tool in tools:
            function = tool["function"]
            converted.append({
                "name": function["name"],
                "description": function.get("description", ""),
                "input_schema": function["parameters"],
            })
        return converted

    def _to_openai_response(self, response):
        text_parts = []
        tool_calls = []

        for block in response.content:
            if block.type == "text":
                text_parts.append(block.text)
            elif block.type == "tool_use":
                tool_calls.append({
                    "id": block.id,
                    "type": "function",
                    "function": {
                        "name": block.name,
                        "arguments": json.dumps(block.input),
                    },
                })

        message = {
            "role": "assistant",
            "content": "\n".join(text_parts) if text_parts else None,
        }
        if tool_calls:
            message["tool_calls"] = tool_calls

        return {
            "id": getattr(response, "id", None),
            "model": getattr(response, "model", self.model),
            "choices": [{
                "index": 0,
                "message": message,
                "finish_reason": "tool_calls" if tool_calls else getattr(response, "stop_reason", "stop"),
            }],
            "usage": getattr(response, "usage", None).model_dump() if getattr(response, "usage", None) else None,
        }
