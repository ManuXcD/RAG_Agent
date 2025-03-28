import requests
import streamlit as st

BASE_API_URL = "http://127.0.0.1:7860"
# FLOW_ID = "cc67f6a9-bcb6-4640-8ca4-bf9bdf24c139"
# ENDPOINT = "insurance_agent" # The endpoint name of the flow

FLOW_ID = "139188c1-8b64-4a9a-b6be-c76f8e2dc1a5"
ENDPOINT = "langflow_chatbot_assistant" 

APPLICATION_TOKEN = st.secrets["APP_KEY"]

def run_flow(message: str) -> dict:   
    api_url = f"{BASE_API_URL}/api/v1/run/{ENDPOINT}"

    payload = {
        "input_value": message,
        "output_type": "chat",
        "input_type": "chat",
    }
    
    headers = {"x-api-key": APPLICATION_TOKEN}
    response = requests.post(api_url, json=payload, headers=headers)
    return response.json()


st.sidebar.header("Welcome!") 
st.sidebar.title("options")

st.title("Medical Insurance Help Assistant.")
st.subheader("I'm here to assist you with your mediclaim insurance query.", divider="blue")

def main():
    clear_button = st.sidebar.button("Clear Conversation", key="clear")
    st.sidebar.markdown("Target Audience : Insured")
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Accept user input
    if prompt := st.chat_input("Please ask your query..."):
        
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)

        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            with st.spinner("Searching..."):
                response = run_flow(prompt)
                # response = response["outputs"][0]["outputs"][0]["results"]["message"]["text"].split("</think>")[-1].strip()
                response = response["outputs"][0]["outputs"][0]["results"]["message"]["text"]
                # Display assistant response in chat message container
                st.markdown(response)
    
        st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    main()