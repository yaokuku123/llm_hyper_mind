import langserve

if __name__ == '__main__':
    client = langserve.RemoteRunnable(url="http://localhost:8000/chainDemo")
    print(client.invoke({"language": "英语", "text": "每一个不曾起舞的日子，都是对生命的辜负"}))
