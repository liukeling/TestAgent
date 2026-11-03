这个项目是练手项目，目的是熟悉agent基础 

环境需要 ollama + python +ollama需要有模型 

参考csdn文章https://blog.csdn.net/qq_26440559/article/details/167495954?spm=1001.2014.3001.5501

主要内容：1.知识库 2.简单对话 3.有记忆长文对话

chromadb_tools 知识库管理工具 - 向量数据库chromadb
function_tools 模型可用函数工具
ollama_tools 模型调用 - 单轮对话、文本向量化处理等和模型交互的工具
common 为全局知识库管理、会话工具调用串联等，依赖上面三个工具
session_tools 自定义长对话 - 带记忆功能，使用sessionId 管理，历史会话当知识库作为记忆存储，保留 近N条对话
main 跑测试接口，使用postMan调用简单调试

接口：testLoadRag
描述：加载知识库文档  D:\\ragFiles路径({chromadb_tools.filePath})下 的文档
请求参数 fileName   文档名（包括后缀）
示例：
localhost:8080/testLoadRag?fileName=test2.txt
加载  D:\\ragFiles\\test2.txt 文档 进行 拆分文档成多个词条 然后每个词条转换向量数据存向量数据库
返回 拆分后的词条集合

接口：chatTest
描述：简单单轮对话，一问一答，根据知识库、工具 回答
请求参数 msg   对话内容
示例：
localhost:8080/chatTest?msg=读取D:\ragFiles目录下的test.txt文件内容
返回
{
    "model": "qwen_instruct:latest",
    "created_at": "2026-11-03T11:01:40.1567697Z",
    "done": true,
    "done_reason": "stop",
    "total_duration": 3651117500,
    "load_duration": 5787400,
    "prompt_eval_count": 1034,
    "prompt_eval_duration": 1308068000,
    "eval_count": 26,
    "eval_duration": 2298513000,
    "message": {
        "role": "assistant",
        "content": "文件D:\\ragFiles\\test.txt的内容是：饿了要吃饭，困了要睡觉，累了要休息。",
        "thinking": null,
        "images": null,
        "tool_name": null,
        "tool_calls": null
    },
    "logprobs": null
}

接口：sessioChatTest
描述：多轮对话 历史对话作为session知识库作为记忆  待续。。。。
示例：无，待续。。。。。