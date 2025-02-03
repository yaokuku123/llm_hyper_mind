from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

load_dotenv()

documents = [
    Document(page_content="狗是伟大的伴侣，以其忠诚和友好而闻名。", metadata={"source": "哺乳动物宠物文档"}),
    Document(page_content="猫是独立的宠物，通常喜欢自己的空间。", metadata={"source": "哺乳动物宠物文档"}),
    Document(page_content="金鱼是初学者的流行宠物，需要相对简单的护理。", metadata={"source": "鱼类宠物文档"}),
    Document(page_content="鹦鹉是聪明的鸟类，能够模仿人类的语言。", metadata={"source": "鸟类宠物文档"}),
    Document(page_content="兔子是社交动物，需要足够的空间跳跃。", metadata={"source": "哺乳动物宠物文档"})
]

if __name__ == '__main__':
    model = ChatOpenAI()
    prompt_template = ChatPromptTemplate.from_messages([
        HumanMessagePromptTemplate.from_template("""
            请使用提供的上下文回答以下的问题：
            {question}
            上下文：
            {context}
        """)
    ])
    parser = StrOutputParser()
    # 构建RAG向量数据库（内存）
    vector_store = Chroma.from_documents(documents=documents, embedding=OpenAIEmbeddings())

    # 从向量数据库中匹配top2相似的Document，分数越低，越相似
    # 示例：
    # [
    #   (Document(metadata={'source': '哺乳动物宠物文档'}, page_content='猫是独立的宠物，通常喜欢自己的空间。'), 0.2780362069606781),
    #   (Document(metadata={'source': '哺乳动物宠物文档'}, page_content='兔子是社交动物，需要足够的空间跳跃。'), 0.41131433844566345)
    # ]
    print("vector_store.similarity_search_with_score: ",
          vector_store.similarity_search_with_score(query="咖啡猫", k=2))

    # 构建检索器，目的是实现chain的链式调用
    retriever = RunnableLambda(func=vector_store.similarity_search).bind(k=1)
    print("retriever.batch: ", retriever.batch(inputs=["咖啡猫", "鲨鱼"]))

    # RunnablePassthrough透传数据
    chain = {"question": RunnablePassthrough(), "context": retriever} | prompt_template | model | parser
    print(chain.invoke("猫是什么？"))
