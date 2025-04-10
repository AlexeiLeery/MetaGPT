"""Simple scorer."""

import json

from pydantic import Field

from metagpt.exp_pool.schema import Score
from metagpt.exp_pool.scorers.base import BaseScorer
from metagpt.llm import LLM
from metagpt.provider.base_llm import BaseLLM
from metagpt.utils.common import CodeParser

SIMPLE_SCORER_TEMPLATE = """
Role: You are a highly efficient assistant, tasked with evaluating a response to a given request. The response is generated by a large language model (LLM). 

I will provide you with a request and a corresponding response. Your task is to assess this response and provide a score from a human perspective.

## Context
### Request
{req}

### Response
{resp}

## Format Example
```json
{{
    "val": "the value of the score, int from 1 to 10, higher is better.",
    "reason": "an explanation supporting the score."
}}
```

## Instructions
- Understand the request and response given by the user.
- Evaluate the response based on its quality relative to the given request.
- Provide a score from 1 to 10, where 10 is the best.
- Provide a reason supporting your score.

## Constraint
Format: Just print the result in json format like **Format Example**.

## Action
Follow instructions, generate output and make sure it follows the **Constraint**.
"""


class SimpleScorer(BaseScorer):
    llm: BaseLLM = Field(default_factory=LLM)

    async def evaluate(self, req: str, resp: str) -> Score:
        """Evaluates the quality of a response relative to a given request, as scored by an LLM.

        Args:
            req (str): The request.
            resp (str): The response.

        Returns:
            Score: An object containing the score (1-10) and the reasoning.
        """

        prompt = SIMPLE_SCORER_TEMPLATE.format(req=req, resp=resp)
        resp = await self.llm.aask(prompt)
        resp_json = json.loads(CodeParser.parse_code(resp, lang="json"))

        return Score(**resp_json)
