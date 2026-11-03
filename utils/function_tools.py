
tool_desc = {
    "read_file":"本地文本文件读取方法"
}
#模型工具方法描述
tools = [
    {
        "type": "function",
        "function":{
            "name":"read_file",
            "description":tool_desc["read_file"],
            "parameters":{
                "type":"object",
                "properties": {
                    "path":{
                        "type":"string",
                        "description":"需要读取文本文件的绝对路径"
                    }
                },
                "required":["path"]
            }
        }
    }
]

#读取文本文件 - 提供给模型使用
def read_file(params):
    full_text = "";
    with open(params["path"],"r",encoding="utf-8") as f:
        full_text =f.read();
    return full_text
#模型可调用方法字典
tool_map={
    "read_file":read_file
}