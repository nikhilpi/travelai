from langchain import LLMChain, PromptTemplate
from langchain.llms import BaseLLM
from langchain.output_parsers import CommaSeparatedListOutputParser

class MetaSheetChain(LLMChain):
    """Chain to generates tasks."""

    @classmethod
    def from_llm(cls, llm: BaseLLM, verbose: bool = True) -> LLMChain:
        """Get the response parser."""
        template = (
            "You are an AI assistant helping a travel agent list options for a given time slot in a travel itinerary."
            " Your job is to create a spreadsheet with columns that helps the travel agent compare options given a request."
            " You must have column for all important deatils about an option that would allow for the agent to make an informed recommendation."
            " Do not include columns for name, address, rating, and price."
            " \nYou have these tools available to add data to the columns: {tools}."
            " \nPlease list the columns you would want to create as a comma sperated list of strings."
            " Be as specific as possible about the columns, using full sentences to describe the data they should contain such as units."
            " Here is the request you are creating columns for: {request}.")


        prompt = PromptTemplate(
            template=template,
            input_variables=[
                "tools",
                "request",
            ],
            output_parser=CommaSeparatedListOutputParser()
        )

        return cls(prompt=prompt, llm=llm, verbose=verbose)