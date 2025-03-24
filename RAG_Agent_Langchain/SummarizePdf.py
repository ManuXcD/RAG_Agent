from langchain_community.document_loaders import PyPDFLoader
from langchain.chains.summarize import load_summarize_chain
from langchain_text_splitters import CharacterTextSplitter
from langchain_ollama import ChatOllama
from langchain.text_splitter import RecursiveCharacterTextSplitter 


def summarize_pdf(file_path: str, chain_type: str = "map_reduce") -> str:
    """
    Summarize a PDF document using LangChain's map-reduce approach
    
    Args:
        file_path: Path to PDF file
        chain_type: Type of summarization chain (default: map_reduce)
    
    Returns:
        str: Generated summary
    """
    # Load PDF document
    loader = PyPDFLoader(file_path)
    documents = loader.load()
    
    # # Split document into chunks
    # text_splitter = CharacterTextSplitter.from_tiktoken_encoder(
    #     chunk_size=1000, chunk_overlap=200
    # )
    # split_docs = text_splitter.split_documents(documents)

    # Split documents into chunks using RecursiveCharacterTextSplitter
    text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,  
            chunk_overlap=200  
    )
    split_docs = text_splitter.split_documents(documents)
    
    # Initialize LLM
    llm = ChatOllama(temperature=0, model_name="deepseek-r1:1.5b")
    
    # Load summarization chain
    chain = load_summarize_chain(
        llm,
        chain_type=chain_type,
        verbose=False
    )
    
    return chain.run(split_docs)

if __name__ == "__main__":
    # Example usage
    summary = summarize_pdf("attention.pdf")
    print("Generated Summary:")
    print(summary)
