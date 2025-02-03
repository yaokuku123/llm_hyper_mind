from dotenv import load_dotenv
from langchain_community.llms.ollama import Ollama
from langchain_core.messages import HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, MessagesPlaceholder, \
    HumanMessagePromptTemplate
from langchain_core.runnables import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI
from langchain_community.chat_message_histories import ChatMessageHistory

load_dotenv()

"""
stores字典用于保存历史记录，所有用户的历史记录都保存到stores，key:sessionID
示例：
{
    '123': InMemoryChatMessageHistory(
            messages=[
                HumanMessage(content='你好，我是yorick'), 
                AIMessage(content='你好，Yorick！很高兴认识你！有什么我可以帮助你的吗？'), 
                HumanMessage(content='我是谁？刚才已经告诉你了对么？'), 
                AIMessage(content='是的，你刚才告诉我你是Yorick。你有什么想聊的或者需要帮助的呢？'), 
                HumanMessage(content='请给我讲一个笑话'), 
                AIMessage(content='好的，给你讲一个笑话：\n\n为什么小鸡过马路？因为要去找答案：为什么要找答案？因为有只小鸭子问它：为什么要找答案？\n\n希望这个笑话能让你开心！有其他问题或者需要帮助的话，随时告诉我哦！')
            ]
    )
}
"""
stores = {}


def get_session_history(session_id: str):
    """
    获取用户的历史记录，接收sessionID返回对应的消息历史记录对象
    """
    if session_id not in stores:
        stores[session_id] = ChatMessageHistory()
    return stores[session_id]


if __name__ == '__main__':
    model = ChatOpenAI()
    # model = Ollama(model="qwen:1.8b")
    prompt_template = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template("你是一个乐于助人的助手。用{language}尽可能的回答所有问题"),
        MessagesPlaceholder(variable_name="history"),
        HumanMessagePromptTemplate.from_template("{text}")
    ])
    parser = StrOutputParser()
    chain = prompt_template | model | parser
    do_message = RunnableWithMessageHistory(
        runnable=chain,
        get_session_history=get_session_history,
        input_messages_key="text",
        history_messages_key="history"
    )
    # 第1轮对话
    rsp = do_message.invoke(
        input={
            "text": [HumanMessage(content="你好，我是yorick")],
            "language": "中文"
        },
        config={
            "configurable": {"session_id": "123"}
        }
    )
    print(rsp)
    # 第2轮对话
    rsp = do_message.invoke(
        input={
            "text": [HumanMessage(content="我是谁？刚才已经告诉你了对么？")],
            "language": "中文"
        },
        config={
            "configurable": {"session_id": "123"}
        }
    )
    print(rsp)
    # 第3轮对话，流式
    for rsp in do_message.stream(
            input={"text": [HumanMessage(content="请给我讲一个笑话")], "language": "中文"},
            config={"configurable": {"session_id": "123"}}
    ):
        print(rsp, end='-')
