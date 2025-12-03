import streamlit as st
from openai import OpenAI

# --- 設定頁面標題 ---
st.set_page_config(page_title="我的完美 AI 助手", page_icon="🤖")
st.title("🤖 AI 聊天機器人 v1.0")

# --- 側邊欄：設定 API Key ---
with st.sidebar:
    api_key = st.text_input("請輸入 OpenAI API Key", type="password")
    st.markdown("[取得 OpenAI API Key](https://platform.openai.com/account/api-keys)")

# --- 步驟 1: 初始化記憶 (Session State) ---
# 如果這是第一次打開頁面，我們需要建立一個空的訊息列表來存放對話
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "system", "content": "你是一個有用且友善的 AI 助手。"}
    ]

# --- 步驟 2: 顯示歷史訊息 ---
# 每次畫面刷新時，重新把過去的對話畫在螢幕上
for msg in st.session_state.messages:
    if msg["role"] != "system": # 不顯示系統設定指令
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

# --- 步驟 3: 處理使用者輸入 ---
if prompt := st.chat_input("請輸入你的問題..."):
    
    if not api_key:
        st.info("請先在左側輸入 API Key 才能開始對話喔！")
        st.stop()

    # 1. 顯示使用者的訊息
    with st.chat_message("user"):
        st.write(prompt)
    
    # 2. 將使用者的訊息加入記憶
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 3. 呼叫 AI 大腦 (OpenAI API)
    client = OpenAI(api_key=api_key)
    
    try:
        with st.chat_message("assistant"):
            stream = client.chat.completions.create(
                model="gpt-4o-mini", # 或使用 gpt-3.5-turbo
                messages=st.session_state.messages,
                stream=True, # 啟用打字機效果
            )
            
            # 接收並顯示 AI 的回應
            response = st.write_stream(stream)
            
        # 4. 將 AI 的回應加入記憶
        st.session_state.messages.append({"role": "assistant", "content": response})

    except Exception as e:
        st.error(f"發生錯誤：{e}")