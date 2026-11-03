import os
from utils.ollama_tools import embed_texts
from utils.ollama_tools import ollama_embed
from utils.ollama_tools import model_chat

from utils.chromadb_tools import filePath
from utils.chromadb_tools import collection
from utils.chromadb_tools import splitter
from utils.chromadb_tools import load_info
from utils.chromadb_tools import save_info

from utils.function_tools import tool_map
from utils.function_tools import tool_desc

#向量库查询
def queryInfos(msg:str):
    q_ver = ollama_embed([msg])
    res = collection.query(
        query_embeddings=q_ver,
        n_results=12
    )
    return res
#解析callTool 参数：resp 模型返回数据，解析他是否需要调用tool; toolMsgs函数词条
def handle_tools(resp, toolMsgs):
    handleInfo = {
        "hasFun": False,
        "function_results":[]
    }
    if resp is not None:
        calls = resp.message.tool_calls;
        if(calls is not None and len(calls) > 0):
            handleInfo["hasFun"] = True
            for call in calls:
                func_name = call.function.name
                func_args = call.function.arguments
                func_method = tool_map[func_name]
                func_result = func_method(func_args)
                tool_msg = {
                    "function":{
                        "name":func_name,
                        "result":func_result
                    }
                }
                handleInfo["function_results"].append(tool_msg)
                #函数调用提示词
                if toolMsgs is not None:
                    func_tip = f"方法：{func_name} 描述：{tool_desc[func_name]} 参数：{func_args} 调用结果：{func_result}"
                    toolMsgs.append(func_tip)
    return handleInfo
#默认rag知识库加载
def msg_default_rag(msg:str):
    #知识库提示内容
    docs = queryInfos(msg)["documents"][0];
    context = "\n".join(docs)
    docMsg = {"role":"system","content":f"""
    以下是知识库检索到的相关文档信息：
    {context}
    """}
    return docMsg
#循环检测是否需要工具调用 - 入参：messages - 会话内容  resp 模型当前返回内容  
#返回：轮询工具调用后的结果；轮询内容会话放置在messages里,工具返回的数据词条加入toolMsgs
def tool_loop_chat(messages,resp,toolMsgs):
    resp_tmp = resp;
    tools_info = handle_tools(resp_tmp,toolMsgs)
    while tools_info["hasFun"]:
        #有工具调用 -组装tool工具返回结果
        tool_results = tools_info["function_results"]
        tool_msg = {
            "role":"tool",
            "content":f"""
            {tool_results}
            """
        }
        #模型请求工具调用的对话信息
        assistant_dict = {
            "role": resp_tmp.message.role,
            "content":resp_tmp.message.content,
            "tool_calls":resp_tmp.message.tool_calls,
        }
        messages.append(assistant_dict)
        messages.append(tool_msg)
        resp_tmp = model_chat(messages);
        tools_info = handle_tools(resp_tmp,toolMsgs)
    return resp_tmp;
#简单模型问答 - 知识库&工具使用
def agent_handle(msg:str):
    #知识库提示内容
    docMsg = msg_default_rag(msg);
    #当前对话内容
    curMsg = {"role":"user","content":msg}
    #组装内容
    messages = [docMsg,curMsg]
    resp = model_chat(messages)
    return tool_loop_chat(messages, resp,None)

#加载 路径下的文档存入 向量库
def loadFiles(fileName:str):
    full_file_path = os.path.join(filePath, fileName);
    full_text = "";
    with open(full_file_path,"r",encoding="utf-8") as f:
        full_text =f.read();
    chunks = splitter.split_text(full_text)
    embeddings=ollama_embed(chunks)
    collection.add(
        ids=[f"{fileName}_{i}" for i in range(len(chunks))],
        documents=chunks,
        embeddings=embeddings
    )
    return chunks
#加载文档 - 读取配置判断是否加载过
def loadFiles_check(fileName:str):
    #读取配置 - 是否加载过，加载过不再处理
    localPropeties = load_info();
    print(localPropeties)
    fileNames = localPropeties.get("fileNames",None)
    has = False;
    curLen = 0
    if fileNames is not None:
        curLen = len(fileNames);
        for n in fileNames:
            has = (has or n==fileName)
    if has:
        print("=====skip...")
        return None;
    chunks = loadFiles(fileName);
    if curLen == 0:
        fileNames = []
        localPropeties["fileNames"]= fileNames
    fileNames.append(fileName);
    #保存配置 - 记录当前rag加载了哪些内容
    save_info(localPropeties)
    return chunks

    