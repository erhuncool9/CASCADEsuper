import os
import time
import traceback

from cascade.generation.executor.LLMCaller import LLMCaller, LLMResponse


class OpenAICompatibleCaller(LLMCaller):
    """
        Adapter for OpenAI and OpenAI-compatible chat completion APIs.

        This covers OpenAI, DeepSeek, vLLM, and other providers that expose a
        /v1/chat/completions compatible endpoint.
    """
    PROVIDER_DEFAULTS = {
        "openai": {
            "api_key_env": "OPENAI_API_KEY",
            "base_url": None,
            "token_parameter": "max_completion_tokens",
            "send_temperature": False,
        },
        "deepseek": {
            "api_key_env": "DEEPSEEK_API_KEY",
            "base_url": "https://api.deepseek.com",
            "token_parameter": "max_tokens",
            "send_temperature": True,
        },
        "openai-compatible": {
            "api_key_env": "OPENAI_API_KEY",
            "base_url": None,
            "token_parameter": "max_tokens",
            "send_temperature": True,
        },
        "vllm": {
            "api_key_env": None,
            "base_url": "http://localhost:8000/v1",
            "token_parameter": "max_tokens",
            "send_temperature": True,
        },
    }

    def __init__(
        self,
        provider="openai",
        max_attempts=1,
        max_tokens=16000,
        temperature=0,
        delay=5,
        dummy=False,
        model="gpt-4o-mini-2024-07-18",
        freq_penalty=0.0,
        base_url=None,
        api_key=None,
        api_key_env=None,
        timeout=60.0,
        token_parameter=None,
        send_temperature=None,
        enable_thinking=None,
    ):
        provider = (provider or "openai").lower()
        defaults = self.PROVIDER_DEFAULTS.get(provider, self.PROVIDER_DEFAULTS["openai-compatible"])

        self.provider = provider
        self.max_attempts = max_attempts
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.delay = delay
        self.freq_penalty = freq_penalty
        self.model = model
        self.token_parameter = token_parameter or defaults["token_parameter"]
        self.send_temperature = defaults["send_temperature"] if send_temperature is None else send_temperature
        self.dummy = dummy
        self.enable_thinking = enable_thinking

        if dummy:
            self.client = None
            return

        try:
            from openai import OpenAI
        except ImportError as exc:
            raise ImportError(
                "The OpenAI-compatible adapter requires the 'openai' package. "
                "Install it with: pip install openai"
            ) from exc

        resolved_base_url = base_url if base_url is not None else defaults["base_url"]
        resolved_api_key_env = api_key_env or defaults["api_key_env"]

        client_kwargs = {"timeout": timeout}
        if resolved_base_url is not None:
            client_kwargs["base_url"] = resolved_base_url

        if resolved_api_key_env:
            client_kwargs["api_key"] = os.environ.get(resolved_api_key_env, api_key)
        else:
            client_kwargs["api_key"] = api_key
        if client_kwargs["api_key"] is None and resolved_base_url is not None:
            client_kwargs["api_key"] = "dummy"

        self.client = OpenAI(**client_kwargs)

    def execute(self, prompt, **kwargs):
        if self.dummy:
            return LLMResponse({
                "choices": [{
                    "message": {"role": "assistant", "content": ""},
                    "finish_reason": "stop",
                }]
            })

        sanitized_prompt = []
        if isinstance(prompt, list):
            for msg in prompt:
                if isinstance(msg, dict):
                    new_msg = msg.copy()               
                    if new_msg.get("content") is None:
                        new_msg["content"] = ""
                    if new_msg.get("role") == "assistant":
                        if "tool_calls" in new_msg and new_msg["tool_calls"] is None:
                            del new_msg["tool_calls"]
                        if "function_call" in new_msg and new_msg["function_call"] is None:
                            del new_msg["function_call"]
                        if "tool_call_id" in new_msg:
                            del new_msg["tool_call_id"]
                            
                    sanitized_prompt.append(new_msg)
                else:
                    sanitized_prompt.append(msg)
        else:
            sanitized_prompt = prompt
            
        if (
            self.model
            and "qwen" in self.model.lower()
            and self.enable_thinking is not None
        ):
            kwargs.setdefault("extra_body", {})
            kwargs["extra_body"].setdefault("chat_template_kwargs", {})
            kwargs["extra_body"]["chat_template_kwargs"]["enable_thinking"] = (
                self.enable_thinking
        )

        attempt = 0
        while attempt < self.max_attempts:
            try:
                request_kwargs = {
                    "model": self.model,
                    "messages": sanitized_prompt,
                    self.token_parameter: self.max_tokens,
                    "frequency_penalty": self.freq_penalty,
                    **kwargs,
                }
                if self.send_temperature:
                    request_kwargs["temperature"] = self.temperature
                    
                print("DEBUG request_kwargs:", {k: v for k, v in request_kwargs.items() if k != "messages"})

                response = self.client.chat.completions.create(**request_kwargs)
                response_data = response.model_dump()
                choice = response_data.get("choices", [{}])[0] if response_data.get("choices") else {}
                message = choice.get("message") or {}
                content = message.get("content") or ""
                print({
                    "id": response_data.get("id"),
                    "model": response_data.get("model"),
                    "finish_reason": choice.get("finish_reason"),
                    "usage": response_data.get("usage"),
                    "content_chars": len(content),
                })
                return LLMResponse(response_data)

            except Exception as e:
                traceback.print_exc()
                print(f"Generation attempt {attempt + 1} failed: {e}")
                attempt += 1
                time.sleep(self.delay)

        raise Exception("Generation failed because of repeated errors.")
