#根据sessionId 存储 会话上下文，并把上下文作为临时知识库，进行调用模型对话 - 长记忆
from utils.chromadb_tools import client
from utils.common import tool_loop_chat
from utils.common import agent_handle
from utils.common import msg_default_rag

#sessionId 知识库 collection
def getCollection(sessionId:str):
    return client.get_or_create_collection(name="session_coll_"+sessionId)
#组装内容 - 默认知识库、历史对话知识库相关内容（记忆功能）、最近N条对话、当前对话、工具调用对话
def session_chat(msg:str,session_id:str):
    #1.知识库提示内容
    docMsg = msg_default_rag(msg);
    #2.历史对话知识库
    session_coll = getCollection(session_id)
    
    #3.最近N条对话
    #4.当前对话内容
    curMsg = {"role":"user","content":msg}
    messages = [docMsg,curMsg]
    resp = model_chat(messages)
    #5.工具调用对话
    tool_tips = [];
    resp_tool = tool_loop_chat(messages, resp,tool_tips)
    #6.知识库存储 1.当前对话信息 2.工具调用信息

    return resp_tool