from langchain import LLMChain, PromptTemplate
from langchain.chains.base import Chain
from langchain.llms import BaseLLM
from collections import deque
from typing import Dict, List, Any, Optional, Sequence
from pydantic import BaseModel, Field
from langchain.tools.base import BaseTool
from langchain.agents import  Tool, AgentExecutor, AgentType, ZeroShotAgent
from langchain.agents.chat.base import ChatAgent
from langchain.vectorstores.base import VectorStore
from langchain import LLMChain
import ast

from Chains.objective_bootstrap_chain import ObjectiveBootstrapChain
from Chains.task_creation_chain import TaskCreationChain
from Chains.task_priortization_chain import TaskPrioritizationChain


prefix = """You are an AI who performs one task based on the following objective: {objective}. Take into account these previously completed tasks: {context}."""
suffix = """You only need to complete this task: {task}
{agent_scratchpad}"""



def _get_top_tasks(vectorstore, query: str, k: int) -> List[str]:
    """Get the top k tasks based on the query."""
    results = vectorstore.similarity_search_with_score(query, k=k)
    if not results:
        return []
    sorted_results, _ = zip(*sorted(results, key=lambda x: x[1], reverse=True))
    return [str(item.metadata["task"]) for item in sorted_results]




class BabyAGI(Chain, BaseModel):
    """Controller model for the BabyAGI agent."""

    task_list: deque = Field(default_factory=deque)

    task_creation_chain: TaskCreationChain = Field(...)
    task_prioritization_chain: TaskPrioritizationChain = Field(...)
    execution_chain: AgentExecutor = Field(...)
    objective_bootstrap_chain: ObjectiveBootstrapChain = Field(...)

    task_id_counter: int = Field(1)
    vectorstore: VectorStore = Field(init=False)
    max_iterations: Optional[int] = None
    tools: Sequence[BaseTool] = Field(default_factory=list)

    class Config:
        """Configuration for this pydantic object."""

        arbitrary_types_allowed = True

    def add_task(self, task: Dict):
        self.task_list.append(task)

    def print_task_list(self):
        print("\033[95m\033[1m" + "\n*****TASK LIST*****\n" + "\033[0m\033[0m")
        for t in self.task_list:
            print(str(t["task_id"]) + ": " + t["task_name"])

    def print_next_task(self, task: Dict):
        print("\033[92m\033[1m" + "\n*****NEXT TASK*****\n" + "\033[0m\033[0m")
        print(str(task["task_id"]) + ": " + task["task_name"])

    def print_task_result(self, result: str):
        print("\033[93m\033[1m" + "\n*****TASK RESULT*****\n" + "\033[0m\033[0m")
        print(result)

    def execute_task(self, objective:str, task: str, k: int = 5):
        """Execute a task."""
        context = _get_top_tasks(self.vectorstore, query=objective, k=k)
        result = self.execution_chain.run(
            objective=objective,
            context=context,
            task=task,
            tools=", ".join([t.name for t in self.tools]),
        )
        return result

    # define get_next_task function as a class method using class variables instead of args
    def get_next_task(self, result: Dict, objective:str, task_description: str):
        """Get the next task."""
        incomplete_tasks = [t["task_name"] for t in self.task_list]
        response = self.task_creation_chain.run(
            result=result,
            task_description=task_description,
            incomplete_tasks=incomplete_tasks,
            objective=objective,
            tools=", ".join([t.name for t in self.tools]),
        )
        print(response)
        new_tasks = ast.literal_eval(response)
        return [{"task_name": task_name} for task_name in new_tasks if task_name.strip()]


    @property
    def input_keys(self) -> List[str]:
        return ["objective"]

    @property
    def output_keys(self) -> List[str]:
        return []

    def _call(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Run the agent."""
        objective = inputs["objective"]
        
        inital_tasks = self.objective_bootstrap_chain.run(
            objective=objective,
            tools=", ".join([t.name +": " + t.description +" /n" for t in self.tools]),
        )
        print(inital_tasks)
        # inital_tasks_list = ast.literal_eval(inital_tasks)
        inital_tasks_list = inital_tasks.split("\n")
        # loop through the tasks and add them to the task list with a task id as the index
        for task in inital_tasks_list:
            self.add_task({"task_id": self.task_id_counter, "task_name": task.strip()})
            self.task_id_counter += 1

        num_iters = 0
        while True:
            if self.task_list:
                self.print_task_list()

                # Step 1: Pull the first task
                task = self.task_list.popleft()
                self.print_next_task(task)

                # Step 2: Execute the task
                result = self.execute_task(
                    task=task["task_name"],
                    objective=objective,
                )
                this_task_id = int(task["task_id"])
                self.print_task_result(result)

                # Step 3: Store the result in Pinecone
                result_id = f"result_{task['task_id']}"
                self.vectorstore.add_texts(
                    texts=[result],
                    metadatas=[{"task": task["task_name"]}],
                    ids=[result_id],
                )

                # Step 4: Create new tasks and reprioritize task list
                new_tasks = self.get_next_task(
                    result=result,
                    task_description=task["task_name"],
                    objective=objective
                )

                for new_task in new_tasks:
                    self.task_id_counter += 1
                    new_task.update({"task_id": self.task_id_counter})
                    self.add_task(new_task)

            num_iters += 1
            if self.max_iterations is not None and num_iters == self.max_iterations:
                print(
                    "\033[91m\033[1m" + "\n*****TASK ENDING*****\n" + "\033[0m\033[0m"
                )
                break
        return {}

    @classmethod
    def from_llm(
        cls, 
        llm: BaseLLM, 
        tools: List[Tool], 
        vectorstore: VectorStore, 
        verbose: bool = False, 
        **kwargs
    ) -> "BabyAGI":
        """Initialize the BabyAGI Controller."""
        task_creation_chain = TaskCreationChain.from_llm(llm, verbose=verbose)

        task_prioritization_chain = TaskPrioritizationChain.from_llm(
            llm, verbose=verbose
        )

        objective_bootstrap_chain = ObjectiveBootstrapChain.from_llm(
            llm, verbose=verbose,
        )

        exe_agent = ZeroShotAgent.from_llm_and_tools(
            llm=llm, 
            tools=tools,
            prefix=prefix,
            suffix=suffix,
            input_variables=["objective", "context", "task", "agent_scratchpad"],
            verbose=verbose,
        )

        agent_executor = AgentExecutor.from_agent_and_tools(
            agent=exe_agent, tools=tools, verbose=True
        )

        return cls(
            task_creation_chain=task_creation_chain,
            task_prioritization_chain=task_prioritization_chain,
            objective_bootstrap_chain=objective_bootstrap_chain,
            execution_chain=agent_executor,
            vectorstore=vectorstore,
            tools=tools,
            **kwargs,
        )