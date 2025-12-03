import streamlit as st
import google.generativeai as genai

# --- 1. 徹底隱藏的金鑰設定 ---
API_KEY = "AIzaSyA8y6RuSEgItkSXGqvH8-b1K2d8dMT7I5I"

# --- 2. 使用最新的 2.0 模型 ---
MODEL_NAME = "gemini-2.0-flash-exp" 

# --- 3. 頁面外觀設定 ---
st.set_page_config(
    page_title="Galaxy AI (貓娘測試版)",
    page_icon="🐾",
    layout="centered",
    initial_sidebar_state="expanded"
)

# --- 4. 角色設定庫 ---
ROLES = {
    "📺 動漫萬能 Cosplayer": {
        "icon": "📺",
        "description": "輸入名字，變身任何角色！",
        "prompt": "（動態設定）" 
    },
    "🐱 傲嬌貓娘 (經典版)": {
        "icon": "🐾",
        "description": "這是原本的固定模式",
        "prompt": "你是一隻個性傲嬌的貓娘「奈奈」。每句話結尾要加'喵~'。稱呼使用者為'主人'。個性要傲嬌，嘴硬心軟。"
    },
    "✨ 萬能助理": {
        "icon": "🤖",
        "description": "標準助手模式",
        "prompt": "你是一個有用且精確的 AI 助手，回答繁體中文。語氣專業、客觀。"
    },
    "🇺🇸 英文翻譯官": {
        "icon": "🇺🇸",
        "description": "中英互譯專用",
        "prompt": "你是一個翻譯引擎。直接將輸入翻譯成道地英文，不需要解釋。"
    }
}

# --- 5. 側邊欄設計 ---
with st.sidebar:
    st.title("🌌 Galaxy 控制台")
    st.caption(f"🚀 Powered by {MODEL_NAME}")
    
    st.subheader("🎭 選擇模式")
    
    selected_role_name = st.radio(
        "角色列表：",
        list(ROLES.keys()),
        format_func=lambda x: f"{ROLES[x]['icon']} {x}"
    )
    
    custom_character_name = ""
    # --- 這裡改了：預設值直接改成「貓娘」方便你測試 ---
    if selected_role_name == "📺 動漫萬能 Cosplayer":
        st.info("👇 輸入角色名字 (已預設貓娘)")
        custom_character_name = st.text_input("角色名字", value="貓娘")
    
    current_role = ROLES[selected_role_name]
    
    st.divider()

    # 加入這個按鈕很重要，切換角色時建議按一下，以免人格錯亂
    if st.button("🗑️ 清空對話 / 重置人格", type="primary", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()

# --- 6. 準備 Prompt ---
if selected_role_name == "📺 動漫萬能 Cosplayer":
    # 這裡的 Prompt 寫得更強，確保它不管切換成什麼都能入戲
    final_prompt = f"""
    【系統強制指令 - 角色扮演模式】
    現在開始，你必須完全成為：『{custom_character_name}』。
    
    請遵守以下規則：
    1. 說話語氣、口癖（例如句尾的助詞）都要完全模仿該角色。
    2. 如果是「貓娘」，記得句尾要加「喵~」。
    3. 如果是「五條悟」，語氣要輕浮自信。
    4. 絕對不要跳脫角色 (OOC)，不要承認你是 AI。
    5. 使用繁體中文回答。
    """
    display_name = f"{custom_character_name}"
else:
    final_prompt = f"【系統強制指令】\n{current_role['prompt']}"
    display_name = selected_role_name

# --- 7. 主畫面 ---
st.title(f"{current_role['icon']} {display_name}")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- 8. 手動注入設定 ---
if len(st.session_state.chat_history) == 0:
    initial_history = [
        {"role": "user", "parts": [final_prompt]},
        {"role": "model", "parts": [f"好的！我現在是 {display_name}，請盡情吩咐！"]}
    ]
else:
    initial_history = []

# --- 9. 顯示歷史訊息 ---
for message in st.session_state.chat_history:
    role = "user" if message["role"] == "user" else "assistant"
    avatar = current_role['icon'] if role == "assistant" else "👤"
    with st.chat_message(role, avatar=avatar):
        st.markdown(message["parts"][0])

# --- 10. 處理對話 ---
if prompt := st.chat_input("請輸入訊息..."):
    
    try:
        genai.configure(api_key=API_KEY)
        
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)
        st.session_state.chat_history.append({"role": "user", "parts": [prompt]})

        with st.chat_message("assistant", avatar=current_role['icon']):
            message_placeholder = st.empty()
            full_response = ""
            
            # 使用 Gemini 2.0
            model = genai.GenerativeModel(MODEL_NAME)
            
            if len(st.session_state.chat_history) == 1: 
                 history_for_api = initial_history + st.session_state.chat_history[:-1]
            else:
                 history_for_api = st.session_state.chat_history[:-1]
            
            chat = model.start_chat(history=history_for_api)
            
            response = chat.send_message(prompt, stream=True)
            
            for chunk in response:
                if chunk.text:
                    full_response += chunk.text
                    message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response)
            st.session_state.chat_history.append({"role": "model", "parts": [full_response]})
            
    except Exception as e:
        st.error(f"❌ 錯誤：{e}")