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
- It can utilize MMR dan Reranking functions.
- 
