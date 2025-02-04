import os

import lancedb
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_community.vectorstores import LanceDB
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough

from langchain_openai import ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()

if __name__ == '__main__':
    model = ChatOpenAI(
        model="glm-4-plus",
        api_key=os.environ["ZHIPU_API_KEY"],
        base_url="https://open.bigmodel.cn/api/paas/v4/"
    )
    loader = TextLoader(file_path="./data/data_input.md", encoding='utf-8')
    docs = loader.load()
    splitter = RecursiveCharacterTextSplitter(chunk_size=100,
                                              chunk_overlap=0,
                                              separators=['/n/n', '/n', '.', '。', '!', '！',
                                                          '?', '？', ',', "，", " ", ""])
    split_texts = splitter.split_documents(docs)
    embeddings = SentenceTransformerEmbeddings(model_name="BAAI/bge-base-zh")
    db_connect = lancedb.connect(uri=os.path.join(os.getcwd(), "lancedb_data_dir"))
    vector_store = LanceDB.from_documents(documents=split_texts,
                                          embedding=embeddings,
                                          connection=db_connect,
                                          table_name="my_ops_git_docs")
    retriever = vector_store.as_retriever()
    prompt_template = ChatPromptTemplate.from_template("""
    Answer the question based only on the following context:
    {context}
    Question: {question}
    """)
    chain = (
            RunnableParallel(context=retriever,
                             question=RunnablePassthrough())
            | prompt_template
            | model
            | StrOutputParser()
    )
    query = "git如何完成版本的回退操作？"
    rsp = chain.invoke(query)
    print(rsp)
