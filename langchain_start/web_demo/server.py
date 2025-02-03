import langserve
from dotenv import load_dotenv
from fastapi import FastAPI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_openai import ChatOpenAI
import uvicorn

load_dotenv()


def translate_chain():
    """
    langchain translate
    """
    model = ChatOpenAI()
    prompt_template = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template("请将以下内容翻译成{language}"),
        HumanMessagePromptTemplate.from_template("{text}")
    ])
    parser = StrOutputParser()
    chain = prompt_template | model | parser
    return chain


if __name__ == '__main__':
    app = FastAPI(title="langchain server", version="v1.0", description="langchain translate service")
    langserve.add_routes(
        app=app,
        runnable=translate_chain(),
        path="/chainDemo"
    )
    uvicorn.run(app=app, host="localhost", port=8000)
