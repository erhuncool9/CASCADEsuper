from cascade.generation.executor.AnthropicCaller import AnthropicCaller
from cascade.generation.executor.OpenAICompatibleCaller import OpenAICompatibleCaller


def create_llm_caller(provider=None, llm_provider=None, **kwargs):
    """
        Creates the configured LLM adapter.

        provider and llm_provider are both supported so config files can use
        either naming style. Unknown providers fall back to the generic
        OpenAI-compatible adapter.
    """
    selected_provider = (llm_provider or provider or "openai").lower()

    if selected_provider in {"anthropic", "claude"}:
        return AnthropicCaller(**kwargs)

    openai_compatible_provider = selected_provider
    if selected_provider in {"openai_compatible", "openai-compatible", "compatible"}:
        openai_compatible_provider = "openai-compatible"

    return OpenAICompatibleCaller(provider=openai_compatible_provider, **kwargs)
