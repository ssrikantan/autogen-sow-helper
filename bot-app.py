import streamlit as st
import asyncio
import autogen

from autogen.agentchat.contrib.retrieve_assistant_agent import RetrieveAssistantAgent
from autogen.agentchat.contrib.retrieve_user_proxy_agent import RetrieveUserProxyAgent
import chromadb


st.title("autogen - SOW AI Assistant")

config_list = autogen.config_list_from_json(
    env_or_file="OAI_CONFIG_LIST",
    file_location=".",
    filter_dict={
        "model": {
            "gpt-4",
            "gpt4",
            "gpt-4-32k",
            "gpt-4-32k-0314",
            "gpt-35-turbo",
            "gpt-3.5-turbo",
        }
    },
)

assert len(config_list) > 0
print("models to use: ", [config_list[i]["model"] for i in range(len(config_list))])


# Accepted file formats for that can be stored in 
# a vector database instance
from autogen.retrieve_utils import TEXT_FORMATS

print("Accepted file formats for `docs_path`:")
print(TEXT_FORMATS)

class TrackableAssistantAgent(RetrieveAssistantAgent):
    def _process_received_message(self, message, sender, silent):
        with st.chat_message(sender.name):
            st.markdown(message)
        return super()._process_received_message(message, sender, silent)


class TrackableUserProxyAgent(RetrieveUserProxyAgent):
    def _process_received_message(self, message, sender, silent):
        with st.chat_message(sender.name):
            st.markdown(message)
        return super()._process_received_message(message, sender, silent)
    

with st.container():
    # for message in st.session_state["messages"]:
    #    st.markdown(message)

    user_input = st.chat_input("Type in your query about creating SOW documents")
    if user_input:
        # create an AssistantAgent instance named "assistant"
        # assistant = TrackableAssistantAgent(
        #     name="assistant", llm_config=llm_config)
        assistant = TrackableAssistantAgent(
        name="assistant", 
        system_message="You are a helpful assistant.",
        llm_config={
            "timeout": 600,
            "cache_seed": 42,
            "config_list": config_list,
            },
        )

        # create a UserProxyAgent instance named "user"
        # user_proxy = TrackableUserProxyAgent(
        #     name="user", human_input_mode="NEVER", llm_config=llm_config)

        user_proxy = TrackableUserProxyAgent(
        name="ragproxyagent",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=10,
        retrieve_config={
            "task": "code",
            "docs_path": "/workspaces/autogen-sow-helper/all_docs/ites/sow",  # change this to your own path, such as https://raw.githubusercontent.com/microsoft/autogen/main/README.md
            "chunk_token_size": 2000,
            "model": config_list[1]["model"],
            "client": chromadb.PersistentClient(path="/tmp/chromadb"),
            "embedding_model": "all-mpnet-base-v2",
            "get_or_create": True,  # set to True if you want to recreate the collection
            },
        )

        # Create an event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        # Define an asynchronous function
        # async def initiate_chat():
        #     await user_proxy.a_initiate_chat(
        #         assistant,
        #         message=user_input,
        #     )

        async def initiate_chat():
            try:
                await user_proxy.initiate_chat(assistant, problem=user_input, search_string="SOW")
            except:
                pass
        # Run the asynchronous function within the event loop
        loop.run_until_complete(initiate_chat())