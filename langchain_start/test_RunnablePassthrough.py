from langchain_core.runnables import RunnableLambda, RunnablePassthrough

use_extra_step = True  # 可以改成 True 来插入额外步骤
# 预处理：去除首尾空格
strip_text = RunnableLambda(lambda x: x.strip())

# 后处理：添加前缀
add_prefix = RunnableLambda(lambda x: f"Processed: {x}")

extra_step = RunnableLambda(lambda x: x.upper()) if use_extra_step else RunnablePassthrough()

pipeline = strip_text | extra_step | add_prefix
output = pipeline.invoke("  Hello, LangChain!  ")
print(output)

chain = {"aa": RunnablePassthrough(), } | RunnableLambda(lambda x: print(x))
chain.invoke("猫是什么？")
