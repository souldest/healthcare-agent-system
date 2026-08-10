from abc import ABC, abstractmethod


class BaseAgent(ABC):

    name = "base_agent"


    @abstractmethod
    def run(
        self,
        input_data
    ):
        pass
