import os
import requests


class LLMProvider:


    def __init__(self):

        self.provider = os.getenv(
            "LLM_PROVIDER",
            "ollama"
        )

        self.model = os.getenv(
            "LLM_MODEL",
            "llama3.2:3b"
        )

        self.ollama_url = os.getenv(
            "OLLAMA_URL",
            "http://localhost:11434/api/generate"
        )


    def generate(
        self,
        prompt: str
    ):

        if self.provider == "ollama":

            try:

                response = requests.post(
                    self.ollama_url,
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,

                        # weniger RAM
                        "options": {
                            "num_ctx": 1024,
                            "temperature": 0.2
                        }
                    },
                    timeout=300
                )


                response.raise_for_status()


                result = response.json()


                return result.get(
                    "response",
                    ""
                )


            except Exception as e:

                return (
                    "LLM unavailable: "
                    + str(e)
                )


        if self.provider == "mock":

            return (
                "Mock LLM response\n\n"
                + prompt
            )


        return "Unknown LLM provider"
