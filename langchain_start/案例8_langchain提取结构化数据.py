from typing import Optional, List

from dotenv import load_dotenv
from langchain_core.messages import SystemMessage
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

load_dotenv()


# 定义最终提取的结构化数据对象
class Person(BaseModel):
    name: Optional[str] = Field(default=None, description="人的名字")
    hair_color: Optional[str] = Field(default=None, description="人的头发颜色")
    height_in_meters: Optional[str] = Field(default=None, description="以米为单位测量人的身高")


class MultiPerson(BaseModel):
    person_list: Optional[List[Person]]


if __name__ == '__main__':
    model = ChatOpenAI()
    # 定义提取数据的Prompt
    prompt_template = ChatPromptTemplate.from_messages([
        SystemMessage(content="""
        你是一个专业的提取算法。
        只从未结构化文本中提取相关信息，如果你不知道提取的属性值，
        返回该属性的值为NULL
        """),
        # MessagesPlaceholder(variable_name="example"), # 按需提供提取结构化数据的案例case
        HumanMessagePromptTemplate.from_template("{text}")
    ])
    # 示例1:单数据对象提取
    chain1 = {"text": RunnablePassthrough()} | prompt_template | model.with_structured_output(schema=Person)
    rsp1 = chain1.invoke("马路上走来一个女生，长长的黑头发披在肩上，大概1米7左右")
    # <class '__main__.Person'> name=None hair_color='黑' height_in_meters='1.7'
    print(type(rsp1), rsp1)

    # 示例2:多数据对象提取
    chain2 = {"text": RunnablePassthrough()} | prompt_template | model.with_structured_output(schema=MultiPerson)
    rsp2 = chain2.invoke(
        "马路上走来一个女生，长长的黑头发披在肩上，大概1米7左右。走在她旁边的是她的男朋友，叫刘海，比她高10厘米")
    # <class '__main__.MultiPerson'> person_list=[Person(name='女生', hair_color='黑', height_in_meters='1.7'), Person(name='刘海', hair_color=None, height_in_meters='1.8')]
    print(type(rsp2), rsp2)
