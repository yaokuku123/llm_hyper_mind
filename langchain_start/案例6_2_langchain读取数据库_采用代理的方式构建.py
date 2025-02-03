from dotenv import load_dotenv
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_community.utilities import SQLDatabase
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import chat_agent_executor

load_dotenv()


def get_db_engine(hostname="localhost", port="3306", database="booktest",
                  username="root", password="199748"):
    mysql_uri = f"mysql+pymysql://{username}:{password}@{hostname}:{port}/{database}?charset=utf8mb4"
    return SQLDatabase.from_uri(mysql_uri)


if __name__ == '__main__':
    model = ChatOpenAI()
    # 获取db连接
    db = get_db_engine()
    print(db.run("select * from EMP limit 3"))
    # 创建工具
    toolkit = SQLDatabaseToolkit(db=db, llm=model)
    tools = toolkit.get_tools()
    # 使用agent完成db整合
    system_prompt = """
    您是一个被设计用来与SQL数据库交互的代理。
    给定一个输入问题，创建一个语法正确的SQL语句并执行，然后查看查询结果并返回答案。
    除非用户指定了他们想要获得的示例的具体数量，否则始终将SQL查询限制为最多10个结果。
    你可以按相关列对结果进行排序，以返回MySQL数据库中最匹配的数据。
    您可以使用与数据库交互的工具。在执行查询之前，你必须仔细检查。如果在执行查询时出现错误，请重写查询并重试。
    不要对数据库做任何DML语句(插入，更新，删除等)。

    首先，你应该查看数据库中的表，看看可以查询什么。
    不要跳过这一步。
    然后查询最相关的表的模式。
    """
    system_message = SystemMessage(content=system_prompt)
    # 创建agent
    agent = chat_agent_executor.create_tool_calling_executor(model=model, tools=tools, prompt=system_message)
    rsp = agent.invoke({"messages": [HumanMessage(content="How many employees are there")]})
    # 示例：There are 14 employees in the database.
    print(rsp["messages"][-1].content)
