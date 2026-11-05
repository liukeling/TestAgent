#根据sessionId 存储 会话上下文，并把上下文作为临时知识库，进行调用模型对话 - 长记忆
from utils.chromadb_tools import client
from utils.common import tool_loop_chat
from utils.common import agent_handle
from utils.common import msg_default_rag
from utils.ollama_tools import ollama_embed
from utils.ollama_tools import model_chat

#对话阈值 - 用户发送消息数量 - 超过就放入历史库
count_flag = 4
#总会话数量 - key session_id value 用户对话次数
session_counts = {

}
#当前会话上下文 - 不包括历史的 、 包括工具调用、系统提示词等
session_messages = {

}
#获取当前sessonId 会话次数 并 +1
def getAndIncreament(session_id):
    cur_count = session_counts.get(session_id,0)
    if cur_count is None:
        cur_count = 0
    cur_count = cur_count + 1
    session_counts[session_id] = cur_count
    return cur_count
#sessionId 知识库 collection
def getCollection(sessionId:str):
    return client.get_or_create_collection(name="session_coll_"+sessionId)
#历史会话处理 - 返回 去除多余会话后的messages 去除的存入知识库
def add_his_msg(curMessages,cur_count,session_id):
    new_cur_messages = curMessages
    if cur_count > count_flag:
        new_cur_messages = []
        session_coll = getCollection(session_id)
        #去除的数量 - 当前窗口内容数量 减去 阈值
        cur_user_len = 0;
        for h in curMessages:
            role = h.get("role",None)
            is_user = role == "user";
            if is_user:
                cur_user_len = cur_user_len+1;
        his_count = cur_user_len - count_flag
        #转换字符串后的历史消息
        str_msgs = [];
        has_chage = False
        for his_msg in curMessages:
            role = his_msg.get("role",None)
            is_user = role == "user";
            if his_count > 0:
                #历史对话转词条
                msg_str = str(his_msg)
                str_msgs.append(msg_str)
                has_chage = True
                if is_user:
                    his_count = his_count - 1
            else:
                if role != "system":
                    new_cur_messages.append(his_msg);
        if has_chage:
            embeddings=ollama_embed(str_msgs)
            session_coll.add(
                ids=[f"{session_id}_{i}" for i in range(len(str_msgs))],
                documents=str_msgs,
                embeddings=embeddings
            )
    return new_cur_messages;
#组装内容 - 默认知识库、历史对话知识库相关内容（记忆功能）、最近N条对话、当前对话、工具调用对话
def session_chat(msg:str,session_id:str):

    #2.历史对话知识库
    cur_count = getAndIncreament(session_id)
    #当前会话窗口
    curMessages = session_messages.get(session_id, [])
    if curMessages is None:
        curMessages = []
    #3.最近N条对话
    new_cur_messages = add_his_msg(curMessages, cur_count,session_id)
    print("new_cur_messages========")
    print(new_cur_messages)
    #4.当前对话内容
    docMsg = msg_default_rag(msg);
    curMsg = {"role":"user","content":msg}
    messages = [docMsg]
    #历史会话知识库 - 记忆功能 - 检索N条相关历史消息
    q_ver = ollama_embed([msg])
    session_coll = getCollection(session_id)
    his_messages = session_coll.query(
        query_embeddings=q_ver,
        n_results=10
    )
    his_msg_docs = his_messages["documents"]
    if len(his_msg_docs) > 0:
        his_msg_content = "\n".join(his_msg_docs[0])
        his_msg_coll = {"role":"system","content":f"""
以下是历史对话知识库检索信息：
{his_msg_content}
"""
        }
        messages.append(his_msg_coll)
    for m in new_cur_messages:
        cur_role = m.get("role",None)
        if cur_role != "system":
            messages.append(m)
    messages.append(curMsg)
    resp = model_chat(messages)
    #5.工具调用对话
    tool_tips = [];
    resp_tool = tool_loop_chat(messages, resp,tool_tips)
    assistant_msg = {
        "role": resp_tool.message.role,
        "content":resp_tool.message.content
    }
    messages.append(assistant_msg)
    session_messages[session_id] = messages;
    print("=============session messages:")
    print(messages)

    return resp_tool