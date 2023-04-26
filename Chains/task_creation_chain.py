from langchain import LLMChain, PromptTemplate
from langchain.llms import BaseLLM


class TaskCreationChain(LLMChain):
    """Chain to generates tasks."""

    @classmethod
    def from_llm(cls, llm: BaseLLM, verbose: bool = True) -> LLMChain:
        """Get the response parser."""
        template = (
            "You are an planner AI that uses the result of an execution agent"
            " to evaluate a to do list that has this objective: {objective},"
            " \nYou have these tools available: {tools}."
            " \nYou goal is add any new tasks that are not already in the to do list using the result last task and the remaining incomplete tasks."
            " Do not overlap with incomplete tasks."
            " Only return any new tasks as an array. If there are no new tasks, return an empty array."
            " For example, if the result is a new task, return ['new task']."
            " For example, if the result is no new task, return []."
            " The last completed task has the result: {result}."
            " \nThis result was based on this task description: {task_description}."
            " \nThese are incomplete tasks: {incomplete_tasks}."
        )

        prompt = PromptTemplate(
            template=template,
            input_variables=[
                "objective",
                "tools",
                "result",
                "task_description",
                "incomplete_tasks",
            ]
        )

        return cls(prompt=prompt, llm=llm, verbose=verbose)