import streamlit as st
import pandas as pd
import plotly.express as px
import base64
from dotenv import load_dotenv
import os
import requests
from openai import AzureOpenAI

params = {}
model_name = ["gpt-4.1", "gtp-4o-mini", "gpt-4o"]
#define url template for OpenAI API with one of the models 'https://chat-ai.cisco.com/openai/deployments/<model name>/chat/completions"
url_template = "https://chat-ai.cisco.com/openai/deployments/{}/chat/completions"
message_with_history = [{
		"role": "system",
		"content": "You are a chatbot"
	},
	{
		"role": "user",
		"content": "who is the president of usa"
	}
]
#get the model name from the selected model
def get_model_name():
    model = st.selectbox("选择模型", model_name)
    if model == "gpt-4.1":
        return "gpt-4.1"
    elif model == "gtp-4o-mini":
        return "gpt-4o-mini"
    elif model == "gpt-4o":
        return "gpt-4o"
    else:
        return None

def init():
    # load .env file and set env variables
    load_dotenv()
    # print environment variables for debugging
    metrics_rest_url = "https://chat-ai.cisco.com/client_metrics"
    client_id = os.getenv("client_id")
    client_secret = os.getenv("client_secret")
    app_key = os.getenv("app_key")
    url = "https://id.cisco.com/oauth2/default/v1/token"

    payload = "grant_type=client_credentials"
    value = base64.b64encode(f'{client_id}:{client_secret}'.encode('utf-8')).decode('utf-8')
    headers = {
        "Accept": "*/*",
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Basic {value}"
    }
    try:
        token_response = requests.request("POST", url, headers=headers, data=payload)
        api_key = token_response.json().get("access_token")
        result = {
            "status_code": token_response.status_code,
            "error": token_response.text if token_response.status_code != 200 else None,
            "client_id": client_id,
            "client_secret": client_secret,
            "app_key": app_key,
            "api_key": api_key
        }

        params["appkey"]=app_key
        metrics_resp = requests.get(
                url=metrics_rest_url,
                params=params,
                headers={
                    "Content-Type": "application/json",
                    "accept" : "application/json",
                    "api-key" : api_key
                }
            )
        result["app_group_info"] = metrics_resp.json().get("app_group_info")
        result["minute_metrics"] = metrics_resp.json().get("minute_metrics")
        return result
    except requests.exceptions.RequestException as e:
        st.error(f"请求失败: {e}")
        return {"status_code": 500, "error": str(e)}

def query_ai(question, params):
    # 这里可以添加调用 ChatGPT API 的代码
    # 例如：response = chatgpt_api.ask(question)
    response = f"这是对您的问题 '{question}' 的回答。"
    return response
st.title("Streamlit Demo: 数据可视化")

init_result = init()
if init_result["status_code"] != 200:
    st.error(f"获取API key失败: {init_result['error']}")
else:
    st.success(f"""
    成功获取API key\n
    app_group_info: {init_result['app_group_info']}\n
    minute_metrics: {init_result['minute_metrics']}
""")
    #select model
    model = get_model_name()
    if model is None:
        st.error("请选择一个有效的模型")
    else:
        st.write(f'{init_result}')
        client = AzureOpenAI(
                azure_endpoint = 'https://chat-ai.cisco.com', 
                api_key=init_result.get("access_token"),  
                api_version="2023-08-01-preview"
            )
        response = client.chat.completions.create(
            model=model, # model = "deployment_name".
            messages=message_with_history,
            user=f'{{"appkey": "{init_result.get("app_key")}"}}',
        )



# 用户输入
st.write("选择一个数据集")
dataset = st.selectbox("数据集", ["Iris", "Tips"])

# 加载数据
if dataset == "Iris":
    df = px.data.iris()
else:
    df = px.data.tips()

# 显示数据
st.dataframe(df.head())

# 交互图表
fig = px.scatter(df, x=df.columns[0], y=df.columns[1], color=df.columns[-1])
st.plotly_chart(fig)

# 用户交2025-06-17 10:54:59互
value = st.slider("选择数据点数量", 10, len(df))
st.write(f"显示前 {value} 行数据")
st.dataframe(df.head(value))

# 输入框，用户可以输入文本
text_input = st.text_input("输入一些文本", "Hello, Streamlit!")
# 增加一个按钮，文本是“拆分步骤”
if st.button("拆分步骤"):
    # 将输入文本按空格拆分成单j
    words = text_input.split()
    st.write("拆分后的单词:", words)

# 输入用户问题的输入框
user_question = st.text_input("请输入您的问题", "如何使用 Streamlit?")
# 点击按钮“提交问题”，访问ChatGPT API， 携带token
if st.button("提交问题"):
    # 这里可以添加调用 ChatGPT API 的代码
    # 例如：response = chatgpt_api.ask(user_question)
    response = f"这是对您的问题 '{user_question}' 的回答。"
    st.write(response)