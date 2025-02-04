import csv
import os
from typing import Optional, Type

import requests
from dotenv import load_dotenv
from langchain_core.callbacks import CallbackManagerForToolRun
from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import chat_agent_executor
from pydantic import BaseModel, Field

load_dotenv()


def get_district_id(district_name: str) -> Optional[str]:
    """
    根据区域名称获取区域编号
    """
    district_map = {}
    with open(file="./data/weather_district_id.csv", mode="r", encoding="utf-8") as f:
        csv_reader = csv.DictReader(f)
        for row in csv_reader:
            district_id = row["district_id"].strip()
            district = row["district"].strip()
            district_map[district] = district_id
    return district_map.get(district_name, None)


class WeatherInputArgs(BaseModel):
    """
    Input的Schema类
    """
    location: str = Field(..., description="用于查询天气的未知信息")


class WeatherTool(BaseTool):
    """
    自定义工具类
    """
    name: str = "weather tool"
    description: str = "可以查询任意位置的当前天气情况"
    args_schema: Type[WeatherInputArgs] = WeatherInputArgs

    def _run(self, location: str, run_manager: Optional[CallbackManagerForToolRun]) -> str:
        district_id = get_district_id(location)
        print(f"需要查询的{location}的地区编码为{district_id}")
        url = f"https://api.map.baidu.com/weather/v1/?district_id={district_id}&data_type=all&ak={os.environ['BAIDU_API_KEY']}"
        rsp = requests.get(url=url)
        data = rsp.json()
        text = data["result"]["now"]["text"]
        temp = data["result"]["now"]["temp"]
        feels_like = data["result"]["now"]["feels_like"]
        return f"位置：{location}，当前天气：{text}，温度：{temp}度，体感温度：{feels_like}."


if __name__ == '__main__':
    model = ChatOpenAI(
        model="glm-4-plus",
        api_key=os.environ["ZHIPU_API_KEY"],
        base_url="https://open.bigmodel.cn/api/paas/v4/"
    )
    tools = [WeatherTool()]
    agent_executor = chat_agent_executor.create_tool_calling_executor(model=model, tools=tools)
    agent_executor_rsp1 = agent_executor.invoke(input={"messages": "中国的首都是哪个城市？"})
    print("agent_executor_rsp1: ", agent_executor_rsp1["messages"])
    agent_executor_rsp2 = agent_executor.invoke(input={"messages": "北京今天的天气怎样？"})
    print("agent_executor_rsp2: ", agent_executor_rsp2["messages"])
