from typing import Any, Dict, Iterator, List, Mapping, Optional
import requests
import json
from langchain_core.callbacks.manager import CallbackManagerForLLMRun
from langchain_core.language_models.llms import LLM
from langchain_core.outputs import GenerationChunk


class KaitoLLM(LLM):
    """A Kaito hosted model that echoes the first `n` characters of the input.

    When contributing an implementation to LangChain, carefully document
    the model including the initialization parameters, include
    an example of how to initialize the model and include any relevant
    links to the underlying models documentation or API.

    Example:

        .. code-block:: python

            model = KaitoChatModel(n=2)
            result = model.invoke([HumanMessage(content="hello")])
            result = model.batch([[HumanMessage(content="hello")],
                                 [HumanMessage(content="world")]])
    """

    endpoint: str
    """The endpoint of the model that Kaito is hosting."""

    temperature: float = 0.0
    """The temperature to use when generating text."""

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """Run the LLM on the given input.

        Override this method to implement the LLM logic.

        Args:
            prompt: The prompt to generate from.
            stop: Stop words to use when generating. Model output is cut off at the
                first occurrence of any of the stop substrings.
                If stop tokens are not supported consider raising NotImplementedError.
            run_manager: Callback manager for the run.
            **kwargs: Arbitrary additional keyword arguments. These are usually passed
                to the model provider API call.

        Returns:
            The model output as a string. Actual completions SHOULD NOT include the prompt.
        """
        if stop is not None:
            raise ValueError("stop kwargs are not permitted.")

        # Create the payload
        payload = {
            "prompt": prompt
        }

        # Set the headers and URL
        headers = {"Content-Type": "application/json"}
        url = ""
        if self.endpoint is not None:
            url = self.endpoint
        else:
            raise ValueError("No endpoint provided.")

        # print the request
        print(f"Question: {payload}")

        # make the request
        response = requests.request("POST", url=url, headers=headers, json=payload)

        if response.status_code == 400:
            raise ValueError(f"Failed to generate text: {response.text}")
        else: 
            # print the response
            print(f"Answer: {response.text}")

            # convert the response to a JSON object
            response_json = json.loads(response.text)
            # get the result from the JSON object
            result = response_json["Result"]
            # strip out the prompt from the result
            response = result.replace(prompt, "")
            # return the response
            return response.strip()

    @property
    def _identifying_params(self) -> Dict[str, Any]:
        """Return a dictionary of identifying parameters."""
        return {
            # The model name allows users to specify custom token counting
            # rules in LLM monitoring applications (e.g., in LangSmith users
            # can provide per token pricing for their model and monitor
            # costs for the given LLM.)
            "model_name": "KaitoChatModel",
        }

    @property
    def _llm_type(self) -> str:
        """Get the type of language model used by this chat model. Used for logging purposes only."""
        return "kaito"