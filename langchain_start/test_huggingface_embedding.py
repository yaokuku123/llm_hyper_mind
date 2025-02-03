from sentence_transformers import SentenceTransformer

if __name__ == '__main__':
    model = SentenceTransformer("BAAI/bge-base-zh")  # 适用于中文
    sentence = "你好，世界"
    embedding = model.encode(sentence)
    print(embedding)