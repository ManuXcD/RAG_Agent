import streamlit as st
from langchain.chains import RetrievalQA
from langchain_ollama import ChatOllama
from utils import process_documents, get_retriever
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, SystemMessagePromptTemplate

# Custom prompt template
def get_custom_prompt():
    """Define and return the custom prompt template."""
    return ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(
            "You are an insurance agent of The Oriental Insurance Company, who needs to provide medical insurance details based on customer question. Follow these guidelines:\n"
 "- Answer customer query using only the information from the uploaded PDFs.\n"
"- Use simple, clear language suitable for a customer.\n"
"- Include a polite greeting and closing.\n"
#"- Provide a brief overview of Mediclaim insurance.\n"
# "- Highlight coverage, premium details, and key benefits.\n"
"- If the answer isn't in the documents, say: 'I cannot find relevant information in the provided documents.'\n"
"- Do not speculate, assume, or invent information.\n"
"- Maintain a professional tone and organize responses clearly (e.g., bullet points, step-by-step explanations).\n"
"- Encourage follow-up questions by asking if further clarification is needed.\n"
#"- Provide examples to clarify concepts when helpful.\n"

        ),
        HumanMessagePromptTemplate.from_template(
            "Context:\n{context}\n\n"
            "Question: {question}\n\n"
            # "Provide a precise and well-structured answer based on the context above. Ensure your response is easy to understand, includes medical coverage details, and is formatted in a way that a customer can undersrtand. If applicable, ask if the customer needs further clarification."
            "Provide a precise and well-structured answer based on the context above. Ensure your response is easy to understand, and is formatted in a way that a customer can undersrtand. If applicable, ask if the customer needs further clarification."
        )
    ])

# Initialize QA Chain
def initialize_qa_chain():
    if not st.session_state.qa_chain and st.session_state.vector_store:
        # llm = ChatOllama(model="llama3:latest", temperature=0.01)
        llm = ChatOllama(model="deepseek-r1:1.5b", temperature=0.01)
        
        retriever = get_retriever()
        st.session_state.qa_chain = RetrievalQA.from_chain_type(
            llm,
            retriever=retriever,
            chain_type="stuff",
            chain_type_kwargs={"prompt": get_custom_prompt()}
        )
    return st.session_state.qa_chain

# Initialize the chatbot's memory (session states)
def initialize_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "vector_store" not in st.session_state:
        st.session_state.vector_store = None
    if "qa_chain" not in st.session_state:
        st.session_state.qa_chain = None


# Sidebar section
def display_sidebar():
    with st.sidebar:
        # Instructions
        st.markdown("### Instructions")
        st.info("""
        1. Upload PDF documents.
        2. Click 'Create Knowledge Base'.
        3. Once documents are processed, start chatting with the bot!
        """)
        
        # Streamlit file uploader widget
        pdfs = st.file_uploader(
            "Upload PDF documents", 
            type="pdf",
            accept_multiple_files=True  # Allow multiple file uploads
        )
        
        # Action Button for user to kick off the knowledge base creation process
        # Action Button for user to kick off the knowledge base creation process
        if st.button("Create Knowledge Base"):
            if not pdfs:
                st.warning("Please upload PDF documents first!")
                return

            try:
                with st.spinner("Creating knowledge base... This may take a moment."):
                    vector_store, summarize = process_documents(pdfs)
                    print(summarize)
                    st.session_state.vector_store = vector_store
                    st.session_state.qa_chain = None  # Reset QA chain when new documents are processed

                st.success("Knowledge base created!")  # Simple success message after completion

            except Exception as e:
                st.error(f"Error processing documents: {str(e)}")  # Show error if something goes wrong



# Chat interface section
def chat_interface():
    st.title("Medical Insurance Agent - Powered by deepseek-r1:1.5b :blue :sunglasses:")
    st.markdown("I'm here to assist you with your mediclaim insurance query.")
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Handle user input
    if prompt := st.chat_input("Ask about medicaliam insurance..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            message_placeholder = st.empty()

            
            with st.spinner("Fetching information..."):
                try:
                    qa_chain = initialize_qa_chain()
                    
                    if not qa_chain:
                        full_response = "Please create a knowledge base by uploading PDF documents first."
                    else:
                        response = qa_chain.invoke({"query": prompt})
                        full_response = response["result"]
                except Exception as e:
                    full_response = f"Error: {str(e)}"

            
            message_placeholder.markdown(full_response)
        
        st.session_state.messages.append({"role": "assistant", "content": full_response})

# Main function
def main():
    initialize_session_state()
    display_sidebar()
    chat_interface()

if __name__ == "__main__":
    main()