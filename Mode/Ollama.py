# from Functions import ActionManage, GetPromptFile, MessagesHistoryManage, RequestAPI, ConfigManage
import json
import re

# 导入Functions
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))  # 添加上级目录到搜索路径
from Functions import ActionManage, GetPromptFile, MessagesHistoryManage, RequestAPI, ConfigManage

BASE_URL = ConfigManage.wnGet('BASE_URL')
MODEL_NAME = ConfigManage.wnGet('MODEL_NAME')


prompt = GetPromptFile.GetPromptFile()
chat_history = [
    {
        "role": "system",
        "content": prompt
    }
]

def round_chat(chat_history: list, user_input, length_limit=10):
    """
    一轮对话，获取
    """
    # 导入全局变量，配置信息
    global BASE_URL, API_KEY, MODEL_NAME
    # 将用户输入加入上下文
    chat_history.append(
        {
            "role": "user",
            "content": user_input
        }
    )
    # 调用RequestAPI模块，向OpenAI API发送请求
    cback = RequestAPI.OpenAI_Format_API(
        base_url=BASE_URL,
        api_key=API_KEY,
        model=MODEL_NAME,
        history=chat_history
    )
    # 将OpenAI API的返回结果转化为文本
    response = RequestAPI.OpenAI_API_Cback_To_Text(cback)
    # 将文本加入上下文
    chat_history.append(
        {
            "role": "assistant",
            "content": response
        }
    )
    MessagesHistoryManage.LimitMessagesHistoryLength(chat_history, length_limit)  # 限制上下文长度
    action = ActionManage.wnGetActionContent(response)  # 获取动作指令
    if action != None:  # 如果存在动作指令，则执行动作，如果没有，则返回None
        action_cback = ActionManage.action_runner(action)
    else:
        action_cback = None
    # 判断是否包含思考过程
    if not RequestAPI.Check_ThinkText(cback):
        return {
            "chat_history": chat_history,
            "action_cback": action_cback
        }
    else:
        think_text = RequestAPI.OpenAI_API_Cback_To_ThinkText(cback)
        return {
            "chat_history": chat_history,
            "think_text": think_text,
            "action_cback": action_cback
        }

def action_round(chat_history: list, action_cback: dict):
    """
    把动作结果给AI
    """
    # 导入全局变量，配置信息
    global BASE_URL, API_KEY, MODEL_NAME
    # 将动作结果加入上下文
    chat_history.append(
        {
            "role": "assistant",
            "content": action_cback["content"]
        }
    )
    # 调用RequestAPI模块，向OpenAI API发送请求
    cback = RequestAPI.OpenAI_Format_API(
        base_url=BASE_URL,
        api_key=API_KEY,
        model=MODEL_NAME,
        history=chat_history
    )
    # 将OpenAI API的返回结果转化为文本
    response = RequestAPI.OpenAI_API_Cback_To_Text(cback)
    # 将文本加入上下文
    chat_history.append(
        {
            "role": "assistant",
            "content": response
        }
    )
    return {
        "chat_history": chat_history
    }

def app():
    """
    主函数
    """
    global chat_history
    while True:
        user_input = input("User >> ")
        result = round_chat(chat_history, user_input)
        if result["chat_history"][-1]["content"] in "</think>":
            print("Assistant >> " + result["chat_history"][-1]["content"].split("</think>")[1])
        else:
            print("Assistant >> " + result["chat_history"][-1]["content"])