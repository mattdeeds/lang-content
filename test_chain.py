from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import PyPDFLoader
from langchain.vectorstores import Chroma
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.agents.agent_toolkits import (
    create_vectorstore_agent,
    VectorStoreToolkit,
    VectorStoreInfo,
)
from langchain.chains import SimpleSequentialChain

# setup the language model
llm = ChatOpenAI(
    model_name="gpt-3.5-turbo-16k",
    max_tokens=5000,
    temperature=0,
)

# load the document
loader = PyPDFLoader("deepmind_compression.pdf")
pages = loader.load_and_split()

print(len(pages))

# set up the vector store
embeddings_model = OpenAIEmbeddings()

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size = 1000,
    chunk_overlap  = 200,
    length_function = len,
    add_start_index = True,
)
documents = text_splitter.split_documents(pages)
db = Chroma.from_documents(documents, embeddings_model, collection_name="deepmind_compression")

# configure the agent and vector store info
vectorstore_info = VectorStoreInfo(
    name="Language_Modeling_Is_Compression",
    description="Research paper from Google DeepMind where they advocate for viewing the prediction problem through the lens of compression and evaluate the compression capabilities of large (foundation) models.",
    vectorstore=db,
)

toolkit = VectorStoreToolkit(vectorstore_info=vectorstore_info, llm=llm)
agent_executor = create_vectorstore_agent(llm=llm, toolkit=toolkit ,verbose=True)

# prompt for the vector store agent
text = "Please create a summary of the Google DeepMind paper highlighting interesting information and author conclusions. Your summaries should be at least 10 sentences long and should highlight exciting information relevent to people in the general AI and LLM community. The summary should be easy to understand and should highlight specific facts and figures from the paper. Do not answer I don't know. Output a summary of the paper."

# setup agent and first chain
chain_one = agent_executor

# prompt template for the second chain
template = """You are an super intelligent AI that has been tasked with writing a twitter thread opitmized for maximum engagement on AI related topics. Given a summary of a research paper, write a twitter thread that will get the most engagement."

Research paper summary:
{summary}
Tweet Thread:"""

prompt_template = PromptTemplate(input_variables=["summary"], template=template)

# setup second chain
chain_two = LLMChain(llm=llm, prompt=prompt_template) 

# prompt template for the third chain
prompt_template_dalle = """You are an super intelligent AI that has been tasked with writing a creating a prompt for OpenAI's Dall-E image generator the prompt should create an interesting AI realated imaged based on the summary of an AI research paper.

Research paper summary:
{summary}
Dall-E Prompt:"""

prompt_template_3 = PromptTemplate(input_variables=["summary"], template=prompt_template_dalle)

# setup third chain
chain_three = LLMChain(llm=llm, prompt=prompt_template_3)

# setup the overall chain
overall_chain = SimpleSequentialChain(
                  chains=[chain_one, chain_two, chain_three],
                  verbose=True)

# run the chain
overall_chain.run(text)