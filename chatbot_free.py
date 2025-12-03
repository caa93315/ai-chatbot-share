import streamlit as st
import google.generativeai as genai

# --- 1. 頁面外觀設定 ---
st.set_page_config(
    page_title="Galaxy AI 萬能夥伴",
    page_icon="🌌",
    layout="centered",
    initial_sidebar_state="expanded"
)

# --- 2. 角色設定庫 ---
ROLES = {
    "📺 動漫萬能 Cosplayer": { # <--- 新增的最強模式
        "icon": "📺",
        "description": "輸入名字，變身任何角色！",
        "prompt": "（動態設定）" # 這裡留空，等一下我們會根據使用者輸入來填寫
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
    st.caption("v3.0 - 動漫無限版")
    
    st.subheader("🎭 選擇模式")
    
    selected_role_name = st.radio(
        "角色列表：",
        list(ROLES.keys()),
        format_func=lambda x: f"{ROLES[x]['icon']} {x}"
    )
    
    # --- 關鍵修改：動漫角色的特殊輸入框 ---
    custom_character_name = ""
    if selected_role_name == "📺 動漫萬能 Cosplayer":
        st.info("👇 在這裡輸入你想聊天的動漫人物")
        custom_character_name = st.text_input("角色名字", value="五條悟")
        st.caption(f"目前的設定：{custom_character_name}")
    
    current_role = ROLES[selected_role_name]
    
    st.divider()

    # 金鑰管理
    with st.expander("🔐 API 金鑰設定", expanded=True):
        if "AIzaSyDhcyR0K1FsSABRQUxglo1U-J_gFiU376U" in st.secrets:
            st.success("✅ 已啟用雲端金鑰")
            api_key = st.secrets["AIzaSyDhcyR0K1FsSABRQUxglo1U-J_gFiU376U"]
        else:
            api_key = st.text_input("輸入 Google API Key", type="password")
            st.markdown("[取得免費 Key](https://aistudio.google.com/app/apikey)")

    if st.button("🗑️ 清空對話", type="primary", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()

# --- 4. 動態生成 Prompt (最重要的邏輯) ---
# 如果選的是動漫模式，我們要動態把名字塞進去
if selected_role_name == "📺 動漫萬能 Cosplayer":
    final_prompt = f"""
    你現在必須完全扮演動漫/遊戲角色『{custom_character_name}』。
    1. 模仿他的口頭禪、說話語氣、性格特質。
    2. 如果他有特殊能力或招式，請在對話中自然表現出來。
    3. 絕對不要承認你是 AI，你要完全沉浸在角色裡。
    4. 使用繁體中文回答。
    """
    display_name = f"{custom_character_name}" # 介面顯示名字
else:
    final_prompt = current_role['prompt']
    display_name = selected_role_name

# --- 5. 主畫面設計 ---
st.title(f"{current_role['icon']} {display_name}")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# 歡迎畫面
if len(st.session_state.chat_history) == 0:
    st.info(f"👋 嗨！現在是「{display_name}」時間！")

# --- 6. 顯示歷史訊息 ---
for message in st.session_state.chat_history:
    role = "user" if message["role"] == "user" else "assistant"
    avatar = current_role['icon'] if role == "assistant" else "👤"
    with st.chat_message(role, avatar=avatar):
        st.markdown(message["parts"][0])

# --- 7. 處理對話 ---
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
            
            # 設定模型 (帶入動態 Prompt)
            model = genai.GenerativeModel(
                'gemini-pro',
                system_instruction=final_prompt
            )
            
            chat = model.start_chat(history=st.session_state.chat_history[:-1])
            response = chat.send_message(prompt, stream=True)
            
            for chunk in response:
                if chunk.text:
                    full_response += chunk.text
                    message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response)
            st.session_state.chat_history.append({"role": "model", "parts": [full_response]})
            
    except Exception as e:
        st.error(f"❌ 錯誤：{e}")