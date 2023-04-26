from langchain import LLMChain, PromptTemplate
from langchain.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)

from langchain.llms import BaseLLM

class ObjectiveBootstrapChain(LLMChain):
    """Chain to generates tasks."""

    @classmethod
    def from_llm(cls, llm: BaseLLM, verbose: bool = True) -> LLMChain:
        """Get the response parser."""
        system_template = (
            "You are an AI travel planner who is an expert at solving travel related problems by"
            " createding steps to solve the problem and then executing them."
            " As a planner you want to balance time, convenience, and the person\'s preferences."
            " \nYou have these tools available to complete the objective: {tools}."
            " \nWhen creating steps, you should rely on the tools as much as possible."
            " Return the steps in an array of strings, one string for each step that can be read by python."
            " The order of the steps in the array is the order of the steps."
            " \nCome up with steps to solve this problem and return only the array of steps: {objective}."
            " \nArray of steps: ")


        human_message_prompt = PromptTemplate(
            template=system_template,
            input_variables=[
                "tools",
                "objective",
            ]
        )

        return cls(prompt=human_message_prompt, llm=llm, verbose=verbose)