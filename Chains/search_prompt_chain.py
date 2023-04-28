from langchain import LLMChain, PromptTemplate
from langchain.llms import BaseLLM
from langchain.output_parsers import CommaSeparatedListOutputParser
    
class SearchPromptChain(LLMChain):
    """Chain to generates tasks."""

    @classmethod
    def from_llm(cls, llm: BaseLLM, verbose: bool = True) -> LLMChain:
        template = """
            Please return a list of search prompts that you would run to get the results for the request: '{request}'
            Each prompt should follow the following format: a type of business (ex: restaurant, coffee shop, museum, etc) followed by a single location. 
            Example input: 'coffee shops in San Francisco'
            Only return a comman seperated list of prompts following that exact format.
        """


        prompt = PromptTemplate(
            template=template,
            input_variables=[
                "request",
            ],
            output_parser=CommaSeparatedListOutputParser()
        )

        return cls(prompt=prompt, llm=llm, verbose=verbose)