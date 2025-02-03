import bs4
from dotenv import load_dotenv
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.history_aware_retriever import create_history_aware_retriever
from langchain.chains.retrieval import create_retrieval_chain
from langchain_chroma import Chroma
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, MessagesPlaceholder, \
    HumanMessagePromptTemplate
from langchain_core.runnables import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.chat_message_histories import ChatMessageHistory

load_dotenv()

# 保存问答的历史记录
stores = {}


def get_session_history(session_id: str):
    if session_id not in stores:
        stores[session_id] = ChatMessageHistory()
    return stores[session_id]


if __name__ == '__main__':
    model = ChatOpenAI()
    # 加载数据
    loader = WebBaseLoader(
        web_paths=["https://lilianweng.github.io/posts/2023-06-23-agent/"],
        bs_kwargs={
            "parse_only": bs4.SoupStrainer(class_=("post-title", "post-content"))
        }
    )
    docs = loader.load()
    # 文档切割
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = splitter.split_documents(docs)
    # 向量库存储
    vector_store = Chroma.from_documents(documents=splits, embedding=OpenAIEmbeddings())
    # 检索器
    retriever = vector_store.as_retriever()
    # 创建模版
    system_prompt = """
    You are an assistant for question-answering tasks.
    Use the following pieces of retrieved context to answer
    the question. If you don't know the answer, say that you
    don't know. Use three sentences maximum and keep the answer concise.\n
    
    {context}
    """
    prompt_template = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(system_prompt),
        MessagesPlaceholder(variable_name="chat_history"),  # 历史上下文记录
        HumanMessagePromptTemplate.from_template("{input}")
    ])
    # 子链(retriever)的提示词模版（辅助检索器理解上下文）
    contextualize_q_system_prompt = """
    Given a chat history and the latest user question
    which might reference context in the chat history,
    formulate a standalone question which can be understood
    without the chat history. Do not answer the question,
    just reformulate it if needed and otherwise return it as is.
    """
    retriever_history_prompt_template = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(contextualize_q_system_prompt),
        MessagesPlaceholder(variable_name="chat_history"),
        HumanMessagePromptTemplate.from_template("{input}")
    ])
    # 创建基于历史上下文理解的检索器（辅助检索器理解上下文）,历史记录默认变量名：chat_history
    history_retriever = create_history_aware_retriever(llm=model, retriever=retriever,
                                                       prompt=retriever_history_prompt_template)

    # 创建chain
    # 创建多文本（Document）上下文处理的chain，上下文默认变量名 context
    combine_docs_chain = create_stuff_documents_chain(llm=model, prompt=prompt_template)
    # 创建基于向量库context检索的chain
    retrieval_chain = create_retrieval_chain(retriever=history_retriever,
                                             combine_docs_chain=combine_docs_chain)
    # 创建含有历史记录的chain
    result_chain = RunnableWithMessageHistory(runnable=retrieval_chain,
                                              get_session_history=get_session_history,
                                              input_messages_key="input",
                                              history_messages_key="chat_history",
                                              output_messages_key="answer")
    # 第1轮对话，可以发现model正常根据上下文理解了输入语义，说明RAG文档检索无误
    rsp1 = result_chain.invoke(
        input={"input": "What is Task Decomposition?"},
        config={"configurable": {"session_id": "yorick123"}}
    )
    print(rsp1["answer"])
    # 第2轮对话，可以发现model正常理解了输入中的单词 it 的指代，说明历史记录无误，并且根据上下文检索无误
    rsp2 = result_chain.invoke(
        input={"input": "What are common ways of doing it?"},
        config={"configurable": {"session_id": "yorick123"}}
    )
    print(rsp2["answer"])
