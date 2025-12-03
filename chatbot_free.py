import streamlit as st
import google.generativeai as genai

# --- 1. 頁面外觀設定 ---
st.set_page_config(
    page_title="Galaxy AI 動漫全能版 (免輸入Key版)",
    page_icon="🌌",
    layout="centered",
    initial_sidebar_state="expanded"
)

# --- 2. 角色設定庫 ---
ROLES = {
    "📺 動漫萬能 Cosplayer": {
        "icon": "📺",
        "description": "輸入名字，變身任何角色！",
        "prompt": "（動態設定）" 
    },
    "✨ 萬能助理": {
        "icon": "🤖",
        "description": "標準助手模式",
        "prompt": "你是一個有用且精確的 AI 助手，回答繁體中文。語氣專業、客觀。"
    },
    "🐱 傲嬌貓娘": {
        "icon": "🐾",
        "description": "會生氣也會撒嬌",
        "prompt": "你是一隻個性傲嬌的貓娘「奈奈」。每句話結尾要加'喵~'。稱呼使用者為'主人'。個性要傲嬌，嘴硬心軟。"
    },
    "🔮 神秘占卜師": {
        "icon": "🔮",
        "description": "探索命運與星座",
        "prompt": "你是一位神秘的占卜師。語氣神秘、優雅。回答時請模擬抽出塔羅牌並解釋含義。"
    },
    "🇺🇸 英文翻譯官": {
        "icon": "🇺🇸",
        "description": "中英互譯專用",
        "prompt": "你是一個翻譯引擎。直接將輸入翻譯成道地英文，不需要解釋。"
    }
}

# --- 3. 側邊欄設計 ---
with st.sidebar:
    st.title("🌌 Galaxy 控制台")
    st.caption("v5.0 - 自動登入版") 
    
    st.subheader("🎭 選擇模式")
    
    selected_role_name = st.radio(
        "角色列表：",
        list(ROLES.keys()),
        format_func=lambda x: f"{ROLES[x]['icon']} {x}"
    )
    
    custom_character_name = ""
    if selected_role_name == "📺 動漫萬能 Cosplayer":
        st.info("👇 在這裡輸入你想聊天的動漫人物")
        custom_character_name = st.text_input("角色名字", value="五條悟")
    
    current_role = ROLES[selected_role_name]
    
    st.divider()

    # --- 這裡是你要求的修改：直接幫你填入 Key ---
    with st.expander("🔐 API 金鑰設定", expanded=True):
        # 這裡我把你的 Key 設為預設值 (value)
        # 這樣你就不用每次都重新貼上了
        api_key = st.text_input(
            "Google API Key (已自動填入)", 
            type="password", 
            value="AIzaSyA8y6RuSEgItkSXGqvH8-b1K2d8dMT7I5I"
        )
        st.caption("⚠️ 警告：Key 已寫入程式碼，請勿隨意分享此檔案給陌生人。")

    # 清除記憶
    if st.button("🗑️ 清空對話 / 套用設定", type="primary", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()

# --- 4. 準備 Prompt (包含動漫設定) ---
if selected_role_name == "📺 動漫萬能 Cosplayer":
    final_prompt = f"""
    【系統強制指令】
    請你現在開始進行角色扮演（Roleplay）。
    你要扮演的角色是：『{custom_character_name}』。
    1. 模仿他的口頭禪、說話語氣、性格特質。
    2. 如果他有特殊能力或招式，請在對話中自然表現出來。
    3. 絕對不要承認你是 AI，你要完全沉浸在角色裡。
    4. 請用繁體中文回答。
    """
    display_name = f"{custom_character_name}"
else:
    final_prompt = f"【系統強制指令】\n{current_role['prompt']}"
    display_name = selected_role_name

# --- 5. 主畫面與標題 ---
st.title(f"{current_role['icon']} {display_name}")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- 6. 核心修改：手動注入 Prompt (解決 404 問題的關鍵) ---
if len(st.session_state.chat_history) == 0:
    initial_history = [
        {"role": "user", "parts": [final_prompt]},
        {"role": "model", "parts": [f"好的！我已經準備好扮演 {display_name} 了。"]}
    ]
else:
    initial_history = []

# --- 7. 顯示歷史訊息 ---
for message in st.session_state.chat_history:
    role = "user" if message["role"] == "user" else "assistant"
    avatar = current_role['icon'] if role == "assistant" else "👤"
    with st.chat_message(role, avatar=avatar):
        st.markdown(message["parts"][0])

# --- 8. 處理對話 ---
if prompt := st.chat_input("請輸入訊息..."):
    
    if not api_key:
        st.warning("⚠️ 請先在左側設定 API Key")
        st.stop()
    
    try:
        genai.configure(api_key=api_key)
        
        # 顯示使用者
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)
        st.session_state.chat_history.append({"role": "user", "parts": [prompt]})

        # 顯示 AI
        with st.chat_message("assistant", avatar=current_role['icon']):
            message_placeholder = st.empty()
            full_response = ""
            
            # 使用 gemini-pro 並手動組合歷史紀錄
            model = genai.GenerativeModel('gemini-pro') 
            
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
        st.caption("如果看到 404 錯誤，請確認網路連線。Key 已經預設填好了。")