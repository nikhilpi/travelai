from langchain import LLMChain, PromptTemplate

from langchain.llms import BaseLLM

class ItineraryModelChain(LLMChain):
    """Chain to generates tasks."""

    @classmethod
    def from_llm(cls, llm: BaseLLM, verbose: bool = True) -> LLMChain:
        """Get the response parser."""
        system_template = (
            "You are an AI planner who is an expert at coming up with a todo list for a given objective."
            " \nYou have these tools available to complete the objective: {tools}."
            " \nWhen creating tasks, you should rely on the tools as much as possible."
            " Return the task items in an array of strings, one string for each task that can be read by python."
            " Do not number the tasks. The order of the tasks in the array is the order of the tasks."
            " Come up with a full todo list as a Python string array for this objective: {objective}.")


        human_message_prompt = PromptTemplate(
            template=system_template,
            input_variables=[
                "tools",
                "objective",
            ]
        )

        return cls(prompt=human_message_prompt, llm=llm, verbose=verbose)