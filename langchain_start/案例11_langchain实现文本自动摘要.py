from dotenv import load_dotenv
from langchain.chains.combine_documents.map_reduce import MapReduceDocumentsChain
from langchain.chains.combine_documents.reduce import ReduceDocumentsChain
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain.chains.llm import LLMChain
from langchain.chains.summarize import load_summarize_chain
from langchain_community.document_loaders import TextLoader
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_text_splitters import CharacterTextSplitter

load_dotenv()


def summary_with_stuff():
    """
    stuff方式整理文档摘要，直接将全部文本放到prompt上下文，该方式未考虑
    文档大小超过模型的上下文token限制的情况
    :return:
    """
    model = ChatOpenAI()
    loader = TextLoader(file_path="./data/data_input.md")
    docs = loader.load()
    chain = load_summarize_chain(llm=model, chain_type="stuff")
    rsp = chain.invoke(docs)
    print(rsp["output_text"])


def summary_with_map_reduce():
    """
    map-reduce的方式获取文本摘要
    :return:
    """
    model = ChatOpenAI()
    loader = TextLoader(file_path="./data/data_input.md")
    docs = loader.load()
    splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    split_docs = splitter.split_documents(docs)
    map_prompt_template = PromptTemplate.from_template("""
        以下是一组文档 documents
        {docs}
        根据这个文档列表，请给出总结摘要:
    """)
    map_chain = LLMChain(llm=model, prompt=map_prompt_template)
    reduce_prompt_template = PromptTemplate.from_template("""
            以下是一组总结摘要
            {docs}
            将这些内容提炼成一个最终的统一的总结摘要:
        """)
    combine_chain = StuffDocumentsChain(llm_chain=LLMChain(llm=model, prompt=reduce_prompt_template),
                                        document_variable_name="docs")
    reduce_chain = ReduceDocumentsChain(
        # 最终调用的chain
        combine_documents_chain=combine_chain,
        # 中间汇总的chain
        collapse_documents_chain=combine_chain,
        # 文档分组token阈值
        token_max=2000
    )
    map_reduce_chain = MapReduceDocumentsChain(
        llm_chain=map_chain,
        reduce_documents_chain=reduce_chain,
        document_variable_name="docs",
        return_intermediate_steps=False
    )
    rsp = map_reduce_chain.invoke(input=split_docs)
    print(rsp["output_text"])


if __name__ == '__main__':
    summary_with_map_reduce()
