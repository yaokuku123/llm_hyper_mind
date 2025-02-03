import os
from functools import partial
from typing import Optional, List

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.messages import SystemMessage
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pydantic import BaseModel, Field

load_dotenv()


# pydantic 标准化检索对象构建
class SearchModel(BaseModel):
    query: str = Field(default=None, description="Similarity search query applied to animal database.")
    publish_year: Optional[int] = Field(default=None, description="year was published.")


def retrieval(vector_store: Chroma, search: SearchModel) -> List[Document]:
    _filter = None
    if search.publish_year:
        _filter = {"publish_year": {"$eq": str(search.publish_year)}}

    return vector_store.similarity_search(query=search.query, k=2, filter=_filter)


def persist_data(persist_dir: str):
    """
    持久化向量数据
    """
    embeddings = OpenAIEmbeddings()
    docs = [
        Document(page_content="狗是伟大的伴侣，以其忠诚和友好而闻名。",
                 metadata={"source": "哺乳动物宠物文档", "publish_year": "2024"}),
        Document(page_content="猫是独立的宠物，通常喜欢自己的空间。",
                 metadata={"source": "哺乳动物宠物文档", "publish_year": "2023"}),
        Document(page_content="金鱼是初学者的流行宠物，需要相对简单的护理。",
                 metadata={"source": "鱼类宠物文档", "publish_year": "2024"}),
        Document(page_content="鹦鹉是聪明的鸟类，能够模仿人类的语言。",
                 metadata={"source": "鸟类宠物文档", "publish_year": "2023"}),
        Document(page_content="兔子是社交动物，需要足够的空间跳跃。",
                 metadata={"source": "哺乳动物宠物文档", "publish_year": "2024"})
    ]
    # 文本切割
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = splitter.split_documents(docs)
    # 向量持久化
    Chroma.from_documents(documents=splits, embedding=embeddings, persist_directory=persist_dir)


def load_vector_db(persist_dir: str):
    """
    加载向量数据
    """
    embeddings = OpenAIEmbeddings()
    vector_store = Chroma(embedding_function=embeddings, persist_directory=persist_dir)
    return vector_store


if __name__ == '__main__':
    persist_dir = "./chroma_data_dir"
    # 持久化向量数据
    if not os.path.exists(persist_dir):
        print("create vector store...")
        persist_data(persist_dir=persist_dir)
    # 加载向量数据
    vector_store = load_vector_db(persist_dir=persist_dir)
    print(vector_store.similarity_search_with_score(query="咖啡猫", k=2))

    model = ChatOpenAI()
    query_vector_prompt = """
    You are an expert at converting user questions into database queries.
    You have access to a database of tutorial videos about animal library.
    Given a question, return a list of database queries optimized to retrieve
    the most relevant results.

    If there are acronyms or words you are not familiar with, do not try to rephrase them.
    """
    # 构建prompt用于转换用户的查询话术为标准化检索对象pydantic结构
    query_vector_template = ChatPromptTemplate.from_messages([
        SystemMessage(content=query_vector_prompt),
        HumanMessagePromptTemplate.from_template("{question}")
    ])
    chain = ({"question": RunnablePassthrough()}
             | query_vector_template
             | model.with_structured_output(schema=SearchModel)  # query='咖啡猫' publish_year=2023
             | partial(retrieval, vector_store)  # 指定结构化检索函数
             )
    rsp = chain.invoke(input="2023年的咖啡猫")
    print(rsp)
