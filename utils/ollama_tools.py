import ollama
import json
from utils.function_tools import tools

#单条doc文本 进行 向量转换
def embed_texts(msg):
    resp = ollama.embed(
        model="nomic-embed-text",
        input=msg
    )
    return resp.embeddings[0]
#使用 ollama的文档转换向量 - 批量
def ollama_embed(texts):
    res_list = []
    for t in texts:
        result = embed_texts(t)
        res_list.append(result)
    return res_list
#模型交互
def model_chat(messages):
    resp = ollama.chat(
        model="qwen_instruct:latest",
        messages=messages,
        tools=tools,
        options={
           "num_ctx":4096,
           "num_gpu":24
        }
    )
    return resp;
