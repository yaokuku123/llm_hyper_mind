from operator import itemgetter

from dotenv import load_dotenv
from langchain.chains.sql_database.query import create_sql_query_chain
from langchain_community.tools import QuerySQLDatabaseTool
from langchain_community.utilities import SQLDatabase
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI

load_dotenv()


def get_db_engine(hostname='localhost', port='3306', database='booktest',
                  username='root', password='199748'):
    """
    获取 DB 链接
    """
    # pip install SQLAlchemy PyMySQL
    mysql_uri = f"mysql+pymysql://{username}:{password}@{hostname}:{port}/{database}?charset=utf8mb4"
    return SQLDatabase.from_uri(mysql_uri)


if __name__ == '__main__':
    model = ChatOpenAI(model="gpt-3.5-turbo")
    # 获取 DB 链接
    db = get_db_engine()

    # 测试执行SQL语句
    print(db.run("select * from EMP limit 3;"))

    # 构建sql查询chain
    sql_query_chain = create_sql_query_chain(llm=model, db=db)

    # 测试调用大模型得到查询SQL语句
    # 示例：SQLQuery: SELECT COUNT(`EMPNO`) AS `TotalEmployees` FROM `EMP`
    print(sql_query_chain.invoke(input={"question": "How many employees are there"}))

    # 定义prompt
    answer_prompt_template = PromptTemplate.from_template(
        """
        给定以下用户问题、SQL语句和SQL执行后的结果，回答用户问题
        Question: {question}
        SQL Query: {query}
        SQL Result: {result}
        回答：
        """
    )

    # 创建执行SQL工具
    execute_sql_tool = QuerySQLDatabaseTool(db=db)

    # chain: 生成SQL，执行SQL
    # itemgetter("query") | execute_sql_tool 获取上一步的query结果，然后传递给sql执行工具获取执行结果
    chain = (RunnablePassthrough.assign(query=sql_query_chain).assign(result=itemgetter("query") | execute_sql_tool)
             | answer_prompt_template
             | model
             | StrOutputParser()
             )
    rsp = chain.invoke(input={"question": "How many employees are there"})
    print(rsp)
