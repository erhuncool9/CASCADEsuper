from abc import ABC, abstractmethod


class LLMResponse:
    """
        Small compatibility wrapper for provider responses.

        CASCADE historically consumed OpenAI ChatCompletion objects via
        model_dump(). Adapters return this wrapper so the rest of the
        generation code can keep using the same response shape.
    """
    def __init__(self, data):
        self.data = data

    def model_dump(self):
        return self.data


class LLMCaller(ABC):
    """
        Abstract base class for prompt executors.
    """
    @abstractmethod
    def execute(self, prompt, **kwargs):
        pass
