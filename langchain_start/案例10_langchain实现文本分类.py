from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

load_dotenv()


class Classification(BaseModel):
    sentiment: str = Field(..., enum=["happy", "neutral", "sad"], description="文本的情感")
    aggressiveness: int = Field(..., enum=[1, 2, 3, 4, 5], description="描述文本的攻击性，数字越大表示越具有攻击性")
    language: str = Field(..., enum=["中文", "英文", "未知"], description="文本使用的语言")


if __name__ == '__main__':
    model = ChatOpenAI(temperature=0)
    tagging_prompt_template = ChatPromptTemplate.from_template(
        """
        从以下段落中提取所需信息。
        只提取 Classification 类中提到的属性
        段落：
        {text}
        """
    )
    chain = tagging_prompt_template | model.with_structured_output(schema=Classification)
    input_text = "中国人民大学的王教授:师德败坏，做出的事情实在让我生气"
    rsp = chain.invoke(input={"text": input_text})
    # sentiment='sad' aggressiveness=5 language='中文'
    print(rsp)
