# Importing Chainlit Library to create a web-based chat interface
import chainlit as cl

# Importing chatbot system and conversation state from workflow.py
from workflow import ChatState, ChatEngine

# Importing types of messages used in the conversation
from langchain_core.messages import HumanMessage, AIMessage

# Importing Runnable to manage chatbot's logic flow
from langchain_core.runnables import Runnable

# These functions run when user starts the chat session
@cl.on_chat_start
async def on_chat_start():
    
    state = {"messages": []} # Create an empty message list to store conversations
    agent = ChatEngine() # Calling the ChatEngine to create a chatbot agent

    compiled_graph = agent.workflow.compile() # Compiling the LangGraph logic workflows used by the chatbot

    cl.user_session.set("graph", compiled_graph) # Save compiled workflows in the session memory
    cl.user_session.set("state", state) # Save initial converstaion state in the session memory

# These functions run everytime a user sends a message
@cl.on_message
async def on_message(message: cl.Message):
    
    graph: Runnable = cl.user_session.get("graph") # Load chatbot workflow from session memory
    state = cl.user_session.get("state")  # Load conversation state from session memory

     # When the workflow is missing, it will show a warning and stop processing
    if graph is None:
        await cl.Message(content="Chatbot is not available. Please restart the session.").send()
        return

    inputs = {"messages": [HumanMessage(content=message.content)]} # Convert the users's message into the proper format for the chatbot to process
    config = {"configurable": {"thread_id": "1"}} # Set a thread ID for session handling

    # Show "Thinking..." while the chatbot is processing the queries 
    ui_msg = cl.Message(content="Thinking...")
    await ui_msg.send()

    try:    
        # Start processing each response in steps (streaming mode)
        async for event in graph.astream(inputs, config, stream_mode="values"):
                        # Showing messages from chatbot gradually, one by one 
            if "messages" in event:
                for m in event["messages"]:
                    if isinstance(m, AIMessage) and m.content:
                        # Display the chatbot's responses/reply token by token                       
                        await ui_msg.stream_token(m.content)

    # Updating the final response in the message box
        await ui_msg.update()

    except Exception as e:
        # If there's an error, this message will be shown in the message box
        ui_msg.content = f"Error: {str(e)}"
        await ui_msg.update()                  
