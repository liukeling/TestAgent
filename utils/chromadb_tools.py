import chromadb
import os
import json
from pathlib import Path

from langchain_text_splitters import RecursiveCharacterTextSplitter

from utils.ollama_tools import embed_texts

#向量数据库
client = chromadb.PersistentClient(path="./test_db")
#全局知识库 - 默认加载
collection = client.get_or_create_collection(name="test_base")

#rag 文档路径
filePath = "D:\\ragFiles\\";
splitter = RecursiveCharacterTextSplitter(chunk_size=600,chunk_overlap=120)

#配置读写- 用于储存当前路径{@filePath}下 文档的加载信息
local_file_properties = "load_infos.json"
def load_info():
    full_file_path = os.path.join(filePath, local_file_properties);
    info_path = Path(full_file_path);
    full_text = "";
    properties = {};
    if info_path.exists():
        with open(full_file_path,"r",encoding="utf-8") as f:
            full_text =f.read();
    if full_text != "":
        properties = json.loads(full_text);
    return properties
#保存配置信息 - 覆盖方式
def save_info(properties):
    full_file_path = os.path.join(filePath, local_file_properties);
    with open(full_file_path,"w",encoding="utf-8") as f:
        json.dump(properties,f,ensure_ascii=False,indent=2)
