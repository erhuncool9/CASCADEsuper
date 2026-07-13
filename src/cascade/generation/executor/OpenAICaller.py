from cascade.generation.executor.OpenAICompatibleCaller import OpenAICompatibleCaller


class OpenAICaller(OpenAICompatibleCaller):
    def __init__(
        self,
        max_attempts=1,
        max_tokens=16000,
        temperature=0,
        delay=5,
        dummy=False,
        model="Qwen/Qwen3-Coder-30B-A3B-Instruct",
        freq_penalty=0.0,
        base_url=None,          
        api_key=None,          
        timeout=60.0,
        **kwargs,
    ):
        provider = "vllm" if base_url is not None else "openai"
        super().__init__(
            provider=provider,
            max_attempts=max_attempts,
            max_tokens=max_tokens,
            temperature=temperature,
            delay=delay,
            dummy=dummy,
            model=model,
            freq_penalty=freq_penalty,
            base_url=base_url,
            api_key=api_key,
            timeout=timeout,
            **kwargs,
        )
