import streamlit as st
import google.generativeai as genai

# --- 1. 頁面設定 ---
st.set_page_config(
    page_title="Gemini 全能助手",
    page_icon="🤖",
    layout="centered"
)

st.title("🤖 Gemini 全能助手")
st.caption("🚀 支援自動金鑰與角色切換 (Flash Model)")

# --- 2. 智慧金鑰管理 (關鍵升級) ---
# 邏輯：先檢查雲端/本地有無設定 Secrets，如果沒有，才顯示輸入框
api_key = None

if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
    # 這裡不顯示 Key，只顯示狀態，保護隱私
    with st.sidebar:
        st.success("✅ 已啟用雲端金鑰 (朋友免輸入)")
else:
    # 如果沒有設定 Secrets，就讓使用者手動輸入
    with st.sidebar:
        st.header("🔐 驗證")
        api_key = st.text_input("AIzaSyDhcyR0K1FsSABRQUxglo1U-J_gFiU376U", type="password")
        st.markdown("[取得免費 Key](https://aistudio.google.com/app/apikey)")

# --- 3. 側邊欄：功能設定 ---
with st.sidebar:
    st.divider()
    st.header("⚙️ 調整大腦")
    
    # 讓使用者選擇 AI 的角色
    role_option = st.selectbox(
        "選擇 AI 角色",
        ("✨ 萬能助理", "🐱 貓娘模式", "🐍 Python 程式導師", "🇺🇸 英文翻譯官"),
        index=0
    
    )
    
    # 根據選擇設定提示詞 (System Prompt)
    system_prompts = {
        "✨ 萬能助理": "你是一個有用的 AI 助手，回答繁體中文。",
        "🐱 貓娘模式": "你是一隻可愛的貓娘，每句話結尾都要加上'喵~'，個性傲嬌。",
        "🐍 Python 程式導師": "你是專業的 Python 專家，只回答程式碼相關問題，並提供範例。",
        "🇺🇸 英文翻譯官": "你是一個翻譯引擎，不管使用者說什麼，都幫我翻譯成道地的英文，不要解釋。"
    }
    current_instruction = system_prompts[role_option]

    st.divider()
    if st.button("🗑️ 清除記憶 / 重置", type="primary"):
        st.session_state.chat_history = []
        st.rerun()

# --- 4. 初始化記憶 ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- 5. 顯示歷史訊息 ---
for message in st.session_state.chat_history:
    role = "user" if message["role"] == "user" else "assistant"
    with st.chat_message(role):
        st.markdown(message["parts"][0])

# --- 6. 處理對話 ---
if prompt := st.chat_input("請輸入訊息..."):
    
    # 檢查是否取得了 Key (不管是自動的還是手動的)
    if not api_key:
        st.warning("⚠️ 請先在左側輸入 API Key，或請管理員設定 Secrets。")
        st.stop()
    
    # 設定 Google API
    try:
        genai.configure(api_key=api_key)
    except Exception as e:
        st.error(f"連線失敗: {e}")
        st.stop()

    # 顯示並儲存使用者訊息
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.chat_history.append({"role": "user", "parts": [prompt]})

    # 呼叫 AI
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            # 設定模型與系統提示 (System Instruction)
            # 注意：Gemini 1.5 Pro/Flash 支援 system_instruction 參數
            model = genai.GenerativeModel(
                'gemini-1.5-flash',
                system_instruction=current_instruction 
            )
            
            # 整理歷史紀錄 (排除系統無法辨識的格式，並限制長度以防錯誤)
            # 這裡我們簡單地傳入過去的對話
            chat = model.start_chat(history=st.session_state.chat_history[:-1])
            
            response = chat.send_message(prompt, stream=True)
            
            for chunk in response:
                if chunk.text:
                    full_response += chunk.text
                    message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response)
            st.session_state.chat_history.append({"role": "model", "parts": [full_response]})
            
        except Exception as e:
            st.error(f"❌ 發生錯誤：{e}")
            st.caption("如果是 Rate Limit 錯誤，請稍等幾秒再試。")