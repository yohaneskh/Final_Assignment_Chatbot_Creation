# Final_Assignment_Chatbot_Creation
This is my final assignment from Qarir Academy (part of Qarir Generator), which is to create a chatbot with certain capabilities. Here are the details of the requirements,

1. Chatbot Features & Capabilities
The chatbot is designed to communicate interactively via a user-friendly Chainlit interface with 2 main capabilities, such as:
A. Retrieval-Augmented Generation (RAG)
i) it can answer questions based on a previously stored pdf file, which is a novel titled Rita Hayworth and The Shawshank Redemption.
ii) the pdf file is chunked and embedded into a Chroma vector database and queried with a search strategy,
- RecursiveCharacterTextSplitter --> chunk_size = 200 and chunk_overlap = 20
- Embedding model --> nomic-embed-text via OllamaEmbeddings

B. Internet Search
- Chatbot can use TavilySearchResult Tool with a configured API key.
- All results will be retrieved from Tavily and ranked before shown to the user.

2. Retriever Function in Details
- Reranking ability is implemented through 'fetch_k' which retrieves more documents before narrowing down to the best 'k'.
- MMR threshold: controlled by 'lamda_mult' with a value of 0.7 to give balanced results between diversity and similarity.

3. LLM Model in Details
The chatbot is powered with MISTRAL model running locally via Ollama,
A. Why Mistral? Mistral is selected because of its balace between speed, quality and its compatibility with my 8GB RAM laptop).
B. Temperature set up at 0.1 in order to prevent any hallucinations and unrelated answers/responses.

4. Summary
- The chatbot made is quite interactive in responding to user's queries and questions.
- It is able to answer questions regarding the novel, Rita Hayworth and The Shawshank Redemption with RAG tool, and to answer questions on general topics and current events from the internet via Tavily tool.
- It can utilize MMR dan Reranking functions in order to present better answers and responses.
- It is compatible with laptops/devices with lower RAM setting. In my case, it is still able to run on my laptop which has 8GB RAM, using Mistral LLM and nomic-embed-text embedding model.

5. Attachments
- main.py --> connect chatbot with workflow.py and Chainlit's user interface
- workflow.py --> organize chatbot's workflow, LLM model, tools and other processing units
- RAG.ipynb --> cleaning and preparing the stored pdf file for the chatbot
- config.ini --> to store senstive information (e.g. Tavily API Key)

7. Disclaimer:
- I made this chatbot by modifying the original framework provided by Mr. Insan Ramadhan as the assigned mentor.
- I also consulted with other participants which have educational and working background in software and data engineering before modifying the framework and codes.
- I also use ChatGPT to check and explain the functions of each line of codes, in order to avoid any potential errors during responsiveness testing session.

Thank you for your kind attention and assistance during the duration of the course.
