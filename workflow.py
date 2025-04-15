# Importing basic system tools for environment setup abd utility functions
import os, functools
from typing import TypedDict, Annotated, Literal, List

# Importing LangChain Hub utility
from langchain import hub

# Importing necessary modules to create and manage the workflow logic
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

# Importing types of messages and tools used in LangChain conversations
from langchain_core.messages import AIMessage, BaseMessage, FunctionMessage, HumanMessage
from langchain_core.runnables import Runnable
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool # Used to turn functions into tools (@tool decorator)
from langchain_core.documents import Document

# Importing local LLM model & text embedding functions
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_chroma import Chroma

# Importing internet search tool to answer general questions
from langchain_community.tools.tavily_search import TavilySearchResults

# Read the configuration file
import configparser 
config = configparser.ConfigParser()
config.read('config.ini')

# Set Tavily API Key to allow Tavily tool to do internet search
os.environ["TAVILY_API_KEY"] = config['DEFAULT']['TAVILY_API_KEY']
tavily_tool = TavilySearchResults(max_results=5)

# Define the class that manages the chatbot's logic and tools
class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

# Creating ChatEngine class with @tool decorator
class ChatEngine:
    def __init__(self):
        self.LLM = ChatOllama(model="mistral", temperature=0.1) # Loading Mistral LLM through Ollama
        self.embeddings = OllamaEmbeddings(model="nomic-embed-text") # Load the embedding model for turning text into numeric vectors
        self.db = Chroma(persist_directory="chromadb", embedding_function=self.embeddings) # Load a local database to store the PDF content using vector embeddings
        
        # Create a pdf document retriever that uses MMR (diverse + relevant results)
        self.retriever = self.db.as_retriever(
            search_type="mmr", # Enabling Max MArginal Relevance (MMR) function to get better answer
            search_kwargs={
                "k": 5, # Return top 5 results 
                "fetch_k": 10, # Fetch 10 results for reranking process
                "lambda_mult": 0.7 # Balancing between relevancies and varieties
    }
)
         # Define available tools for the agent to use
        self.tools = [self.search_pdf, self.internet_search]

        # Define the behavior and rules of the chatbot
        self.system_message = """ 
                                  You're a storyteller with a sharp eye for detail.
                                  You're given a question and a context.
                                  Only use what's in the context—no guesses, no outside knowledge.
                                  
                                  Examples are as following,
                                  Question: Who is Andy's best friend in Shawshank Redemption novel?
                                  Context: Use search_pdf tool to retrieve from the novel Rita Hayworth and The Shawshank Redemption novel.
                                  Answer: Red is Andy's best friend.

                                  Question: Who is the current president of Indonesia?
                                  Context: Use internet_search tool for current events or general topics.
                                  Answer: As of now, Prabowo Subianto is the president.
                                  
                                  ALWAYS answer in English.
                                  NEVER mention your tools, methods and models.
                                  Use tools appropriately.
                                  """

        self.agent = self.create_react_agent(self.LLM, self.tools, self.system_message) # Create the language agent using tools and prompt rules
        self.workflow = self.create_chain(ChatState) # Create the chatbot's workflow using LangGraph

    @tool # Tool to search information from internally stored documents
    def search_pdf(self, query: str) -> str:
        """Use this tool to answer questions about the Rita Hayworth and The Shawshank Redemption novel."""
        docs = self.retriever.invoke(query) # Use retriever function with MMR to get answers
        return "\n\n".join(doc.page_content for doc in docs) if docs else "No relevant info found."

    @tool # Tool to search the internet for current information
    def internet_search(self, query: str) -> str:
        """Use this tool to answer questions about current events or general topics."""
        try:
            results = tavily_tool.invoke({"query": query})
            return results["results"][0]["content"] if results["results"] else "No internet result found."
        except Exception as e:
            return f"Internet search failed: {str(e)}"
    
    # A function to create a react-style agent that uses provided tools
    def create_react_agent(self, llm, tools, system_message: str):
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_message),
            MessagesPlaceholder(variable_name="messages") # Use conversation history
        ])
        return prompt | llm.bind_tools(tools, tool_choice="auto")

    # Processing one step of the agent logic
    def agent_node(self, state, agent, name):
        result = agent.invoke(state)
        if isinstance(result, FunctionMessage):
            return {"messages": [result]}
        result = AIMessage(**result.dict(exclude={"type", "name"}), role=name, name=name)
        return {"messages": [result]}

    # Determining whether the agent needs to call a tool or just end
    def router(self, state) -> Literal["call_tool", "__end__"]:
        messages = state["messages"]
        last = messages[-1]
        return "call_tool" if last.tool_calls else "__end__"

    # Create the complete LangGraph workflow with nodes and routing logic
    def create_chain(self, ChatState):
        agent_fn = functools.partial(self.agent_node, agent=self.agent, name="smart_agent")
        workflow = StateGraph(ChatState) # Initialize workflow with message state
        workflow.add_node("agent", agent_fn) # A node to handle thinking and talking
        workflow.add_node("tool", ToolNode(self.tools)) # A node to use tools
        workflow.set_entry_point("agent") # Start from agent node
        workflow.add_conditional_edges("agent", self.router, {"call_tool": "tool", "__end__": END}) # Choosing the next step
        workflow.add_edge("tool", "agent")  # Going back to agent after tool is used
        return workflow  # Return and repeat the whole workflow