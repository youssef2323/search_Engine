import streamlit as st
from langchain_groq import ChatGroq
from langchain_community.utilities import ArxivAPIWrapper, WikipediaAPIWrapper
from langchain_community.tools import (
    ArxivQueryRun,
    WikipediaQueryRun,
    DuckDuckGoSearchRun,
)
from langchain.agents import initialize_agent, AgentType
from langchain.callbacks import StreamlitCallbackHandler
from langchain.tools import Tool
import os
from dotenv import load_dotenv

##code updated
######

# Custom search function to handle DuckDuckGo errors
def safe_search(query):
    try:
        search_tool = DuckDuckGoSearchRun()
        return search_tool.run(query)
    except Exception as e:
        return f"Search temporarily unavailable. Error: {str(e)}"


## Arxiv and Wikipedia Tools
arxiv_wrapper = ArxivAPIWrapper(top_k_results=1, doc_content_chars_max=200)
arxiv = ArxivQueryRun(api_wrapper=arxiv_wrapper)

wiki_wrapper = WikipediaAPIWrapper(top_k_results=1, doc_content_chars_max=200)
wiki = WikipediaQueryRun(api_wrapper=wiki_wrapper)

# Create a custom search tool with error handling
search = Tool(
    name="Search",
    description="Search the web for current information",
    func=safe_search,
)

st.title("🦜 Langchain - Chat with search")

"""
In this example, I'm using `StreamlitCallbackHandler` to display the thoughts and actions of an agent in an interactive Streamlit app.
Try more LangChain 🤝 Streamlit Agent examples at [github.com/langchain-ai/streamlit-agent](https://github.com/langchain-ai/streamlit-agent).
"""

## Sidebar for settings
st.sidebar.title("Settings")
api_key = st.sidebar.text_input("Enter your Groq API Key:", type="password")

# Add API key validation
if api_key:
    if not api_key.startswith("gsk_"):
        st.sidebar.error("⚠️ Groq API keys should start with 'gsk_'")
    elif len(api_key) < 50:
        st.sidebar.error("⚠️ API key seems too short. Please check your key.")
    else:
        st.sidebar.success("✅ API key format looks correct")

if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {
            "role": "assistant",
            "content": "Hi, I'm a chatbot who can search the web. How can I help you?",
        }
    ]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input(placeholder="What is machine learning?"):
    if not api_key:
        st.error("Please enter your Groq API key in the sidebar to continue.")
        st.stop()

    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    try:
        # Initialize the LLM with error handling
        llm = ChatGroq(
            groq_api_key=api_key, model_name="llama-3.3-70b-versatile", streaming=True
        )

        tools = [search, arxiv, wiki]

        search_agent = initialize_agent(
            tools,
            llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            handling_parsing_errors=True,
            verbose=True,
            max_iterations=3,
            early_stopping_method="generate",
        )

        with st.chat_message("assistant"):
            st_cb = StreamlitCallbackHandler(st.container(), expand_new_thoughts=False)
            try:
                # Pass only the current prompt, not the entire message history
                response = search_agent.run(prompt, callbacks=[st_cb])
                st.session_state.messages.append(
                    {"role": "assistant", "content": response}
                )
                st.write(response)
            except Exception as e:
                error_msg = f"An error occurred: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append(
                    {"role": "assistant", "content": error_msg}
                )

    except Exception as e:
        if "401" in str(e) or "Invalid API Key" in str(e):
            st.error(
                "🔑 Invalid API Key. Please check your Groq API key and try again."
            )
            st.info(
                "💡 Make sure your API key is correct and has the proper permissions."
            )
        else:
            st.error(f"An error occurred: {str(e)}")
