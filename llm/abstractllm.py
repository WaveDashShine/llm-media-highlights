from abc import ABC, abstractmethod

from llm.prompts import PromptType


class AbstractLlm(ABC):

    @abstractmethod
    def generate(self, file_path: str, prompt_type: PromptType) -> str:
        """
        Runs the prompt registered for prompt_type over the subtitle file
        and returns the LLM response.
        :param file_path: path to a .srt (or plain text) subtitle file
        :param prompt_type: which prompt from llm/prompts.py to run
        """
        pass

    def get_highlights(self, file_path: str) -> str:
        """
        Backwards-compatible convenience wrapper for the highlights prompt.
        """
        return self.generate(file_path=file_path, prompt_type=PromptType.HIGHLIGHTS)

    def get_story(self, file_path: str) -> str:
        """
        Convenience wrapper for the story prompt.
        """
        return self.generate(file_path=file_path, prompt_type=PromptType.STORY)
