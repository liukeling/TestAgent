from typing import Annotated
from fastapi import FastAPI,Header
from pydantic import BaseModel

from utils.common import agent_handle
from utils.common import queryInfos
from utils.common import loadFiles_check

from utils.session_tools import session_chat

app = FastAPI(title="Test")

#全局知识库加载 D:\\ragFiles\\fileName  @{chromadb_tools.filePath}
@app.get("/testLoadRag")
def testLoadRag(fileName:str):
    chunks = []
    if fileName:
        chunks = loadFiles_check(fileName)
    return chunks
#测试对话 - 简单对话
@app.get("/chatTest")
def chatTest(msg:str):
    if msg:
        return agent_handle(msg);
    return {"test":"data Info"+msg}

#测试对话 - sessionId长对话
@app.get("/sessioChatTest")
def sessioChatTest(
    msg:str,
    session_id:Annotated[str|None,Header(alias="session_id")]=None
):
    if msg:
        return session_chat(msg,session_id);
    return {"test":"data Info"+msg}
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app",host="127.0.0.1",port=8080,reload=True)