import groq
import streamlit as st
from groq import Groq
import httpx
import ssl
import os
from dotenv import load_dotenv


# Load Environment Variables
load_dotenv()

# A simple check:
# groq_key = st.secrets.get("GROQ_API_KEY")
groq_key = os.environ.get("GROQ_API_KEY")

if not groq_key:
    st.error("GROQ_API_KEY is missing!")

# creates groq client with custom httpx client
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

http_client = httpx.Client(verify=False)  # WARNING: Disabling SSL verification for testing
client = Groq(api_key=groq_key, http_client=http_client)

# Page Header
st.title("Vikram's Chatbot")
st.write("Chatbot powered by Groq.")
st.divider()

# Sidebar
st.sidebar.title("Chats")


# Session State
if "default_model" not in st.session_state:
    st.session_state["default_model"] = "llama-3.1-8b-instant"

if "messages" not in st.session_state:
    st.session_state["messages"] = []

print(st.session_state)


# Display the messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])


# Chat input for user message
if prompt := st.chat_input():
    # append message to message collection
    st.session_state.messages.append({"role": "user", "content": prompt})

    # display the new message
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display the assistant response from the model
    with st.chat_message("assistant"):
        # place holder for the response text
        response_text = st.empty()

        # Call the Groq API
        try:
            completion = client.chat.completions.create(
                model=st.session_state.default_model,
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                stream=True
            )

            full_response = ""

            for chunk in completion:
                content = chunk.choices[0].delta.content or ""
                full_response += content
                response_text.markdown(full_response)

            # add full response to the messages
            st.session_state.messages.append(
                {"role": "assistant", "content": full_response})

        except groq.APIConnectionError as e:
            st.error(
                f"Connection error: Unable to connect to Groq API. Please check your internet connection and API key.")
            print(f"Connection error: {e}")
        except groq.AuthenticationError as e:
            st.error(
                "Authentication error: Invalid API key. Please check your GROQ_API_KEY.")
            print(f"Authentication error: {e}")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            print(f"Error: {e}")
