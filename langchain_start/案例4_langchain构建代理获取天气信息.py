from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_community.tools import TavilySearchResults
from langgraph.prebuilt import chat_agent_executor

load_dotenv()

if __name__ == '__main__':
    model = ChatOpenAI()
    # 构建工具，Tavily用于网络检索相关内容
    search = TavilySearchResults(max_results=2)
    tools = [search]

    # 构建绑定工具的LLM，可以自主调用工具
    # model_with_tools = model.bind_tools(tools)
    # rsp1 = model_with_tools.invoke("中国的首都是哪个城市？")
    # print("rsp1:\n", "model result content: ", rsp1.content, "\n tool result content: ", rsp1.tool_calls)
    # rsp2 = model_with_tools.invoke("北京今天的天气怎样？")
    # print("rsp2:\n", "model result content: ", rsp2.content, "\n tool result content: ", rsp2.tool_calls)

    # 构建代理agent
    agent_executor = chat_agent_executor.create_tool_calling_executor(model=model, tools=tools)
    # 结果：[HumanMessage(),AIMessage(),ToolMessage()]
    # 如果LLM无法直接回答问题会尝试调用工具，若LLM可以直接回答则结果为：AIMessage，若调用工具得到结果为：ToolMessage
    agent_executor_rsp1 = agent_executor.invoke(input={"messages": "中国的首都是哪个城市？"})
    print("agent_executor_rsp1: ", agent_executor_rsp1["messages"])
    agent_executor_rsp2 = agent_executor.invoke(input={"messages": "北京今天的天气怎样？"})
    print("agent_executor_rsp2: ", agent_executor_rsp2["messages"])
