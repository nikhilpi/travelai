from langchain import PromptTemplate
from langchain.chains.base import Chain
from langchain.schema import BaseLanguageModel
from typing import Dict, List, Any, Optional, Sequence
from pydantic import BaseModel, Field
from langchain.tools.base import BaseTool
from langchain.utilities import GooglePlacesAPIWrapper
from langchain.agents import initialize_agent, AgentType, Tool

from Chains.meta_sheet_chain import MetaSheetChain
from Chains.search_prompt_chain import SearchPromptChain


class OptionsGeneratorChain(Chain, BaseModel):

    meta_sheet_chain: MetaSheetChain = Field(...)
    search_prompt_chain: SearchPromptChain = Field(...)
    tools: Sequence[BaseTool] = Field(default_factory=list)
    llm: BaseLanguageModel = Field(...)

    class Config:
        """Configuration for this pydantic object."""
        arbitrary_types_allowed = True

    @property
    def input_keys(self) -> List[str]:
        return ["request"]

    @property
    def output_keys(self) -> List[str]:
        return []

    def _call(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Run the agent."""
        request = inputs["request"]
        places = GooglePlacesAPIWrapper()

        result_columns = self.meta_sheet_chain.predict_and_parse(
            request=request, 
            tools=[t.name +": " + t.description +" /n" for t in self.tools]
        )
        
        prompts = self.search_prompt_chain.predict_and_parse(request=request)
        options = []
        for prompt in prompts:
            search_results = places.google_map_client.places(prompt)
            if len(search_results["results"]) > 0:
                #json parsing results
                for result in search_results["results"]:
                    option = {
                        "name": result["name"] if "name" in result else None,
                        "address": result["formatted_address"] if "formatted_address" in result else None,
                        "rating": result["rating"] if "rating" in result else None,
                        "reviews": result["reviews"] if "reviews" in result else None,
                        "price_level": result["price_level"] if "price_level" in result else None,
                        "place_id": result["place_id"] if "place_id" in result else None,
                        "user_ratings_total": result["user_ratings_total"] if "user_ratings_total" in result else None,
                    }
                    for key in result_columns:
                        option[key] = None
                    options.append(option)

        agent = initialize_agent(self.tools, self.llm, agent=AgentType.CHAT_ZERO_SHOT_REACT_DESCRIPTION, verbose=True)


        template = """
        You are an AI assistant that must fill out missing fields in a spreadsheet for a travel agent using tools. 
        Here is the row you are filling out: {object}
        ONLY return value for this field: {field}
        If you can not fill out the field, return 'None'
        Some columns may be duplicated in the spreadsheet, but you should only fill out the first instance of the column.
        """

        prompt = PromptTemplate(
            input_variables=["object", "field"],
            template=template,
        )

        for option in options[0:1]:
            for key in option:
                if option[key] is None:
                    input = prompt.format(object=option, field=key)
                    try:
                        result = agent.run(input)
                    except:
                        print("error")
                    print(result)

    @classmethod
    def from_llm(
        cls, 
        llm: BaseLanguageModel, 
        tools: List[Tool], 
        verbose: bool = False, 
        **kwargs
    ) -> "OptionsGeneratorChain":
        meta_sheet_chain = MetaSheetChain.from_llm(llm=llm, verbose=verbose)
        search_prompt_chain = SearchPromptChain.from_llm(llm=llm, verbose=verbose)


        return cls(
            meta_sheet_chain=meta_sheet_chain,
            search_prompt_chain=search_prompt_chain,
            tools=tools,
            llm=llm,
            **kwargs,
        )