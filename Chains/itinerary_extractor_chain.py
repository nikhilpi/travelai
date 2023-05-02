

from langchain.chains.summarize import load_summarize_chain
from langchain.chains.combine_documents.base import BaseCombineDocumentsChain
from langchain.base_language import BaseLanguageModel
from typing import Any, Mapping, Optional, Protocol
from itinerary_extractor_prompts import question_prompt, refine_prompt

def load_itenrary_extractor_chain(
    llm: BaseLanguageModel,
    verbose: Optional[bool] = None,
    **kwargs: Any,
) -> BaseCombineDocumentsChain:
    return load_summarize_chain(
        llm=llm,
        chain_type="refine", 
        question_prompt=question_prompt, 
        refine_prompt=refine_prompt,
        verbose=verbose,
        **kwargs)