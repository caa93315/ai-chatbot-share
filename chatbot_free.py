import streamlit as st
import google.generativeai as genai
import time

# --- 1. 頁面設定 ---
st.set_page_config(
    page_title="Gemini 免費 AI 助手",
    page_icon="✨",
    layout="centered"
)

st.title("✨ Gemini 免費無限聊")
st.caption("🚀 使用 Google Gemini Pro 模型 (Free Tier)")

# --- 2. 側邊欄設定 ---
with st.sidebar:
    st.header("⚙️ 設定")
    # 這裡讓使用者輸入 Google 的 Key
    google_api_key = st.text_input("Google API Key", type="password", help="AIzaSyDhcyR0K1FsSABRQUxglo1U-J_gFiU376U")
    st.markdown("[取得免費 Key](https://aistudio.google.com/app/apikey)")
    
    st.divider()
    
    # 清除記憶按鈕
    if st.button("🗑️ 清除對話", type="primary"):
        st.session_state.chat_history = []
        st.rerun()

# --- 3. 初始化記憶 ---
# Gemini 的記憶格式跟 OpenAI 不太一樣，我們這裡用 Google 官方推薦的方式管理
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- 4. 顯示歷史訊息 ---
# 遍歷歷史紀錄並畫在螢幕上
for message in st.session_state.chat_history:
    # Google 的角色名稱是 'user' 和 'model'，我們轉換一下顯示名稱
    role = "user" if message["role"] == "user" else "assistant"
    with st.chat_message(role):
        st.markdown(message["parts"][0])

# --- 5. 處理對話 ---
if prompt := st.chat_input("輸入你想問的事..."):
    
    # 檢查 Key
    if not google_api_key:
        st.warning("⚠️ 請先在左側輸入 Google API Key 喔！")
        st.stop()
    
    # 設定 Google API
    try:
        genai.configure(api_key=google_api_key)
    except Exception as e:
        st.error(f"API Key 設定失敗: {e}")
        st.stop()

    # 顯示使用者輸入
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # 加入歷史紀錄 (暫存顯示用)
    st.session_state.chat_history.append({"role": "user", "parts": [prompt]})

    # 呼叫 Gemini 大腦
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            # 初始化模型 (gemini-1.5-flash 是目前最快且免費額度高的模型)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            # 建立聊天物件 (帶入過去的歷史紀錄)
            chat = model.start_chat(history=st.session_state.chat_history[:-1]) # 傳入除了最新這句以外的歷史
            
            # 發送訊息並取得串流回應
            response = chat.send_message(prompt, stream=True)
            
            # 顯示打字機效果
            for chunk in response:
                if chunk.text:
                    full_response += chunk.text
                    message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response)
            
            # 將 AI 的回應加入記憶
            st.session_state.chat_history.append({"role": "model", "parts": [full_response]})
            
        except Exception as e:
            st.error(f"❌ 發生錯誤：{e}")
            # 這裡常見的錯誤可能是 Free Tier 的速率限制 (Rate Limit)
            # 如果聊太快，Google 會暫時擋一下，稍等幾秒就好