import streamlit as st
import json
import os
import base64
from datetime import datetime

# --- 1. CONFIGURATION ---
STORE_LAYOUTS = {
    "New World (Milford)": ["Fruit & Veg", "Fish", "Deli", "Meat", "Specialty", "Eggs", "Bread", "Baking", "Crackers", "Soft Drinks", "Canned Goods", "Pasta/Rice", "Oils", "Toiletries", "Cat", "Household", "Milk", "Dairy", "Dips", "Frozen", "Alcohol"],
    "Pack N Save (Wairau)": ["Fruit & Veg", "Fish", "Dairy", "Dips", "Meat", "Deli", "Milk", "Soft Drinks", "Bread", "Eggs", "Toiletries", "Baking", "Crackers", "Canned Goods", "Pasta/Rice", "Oils", "Household", "Cat", "Alcohol", "Frozen", "Specialty"],
    "Woolworths (Milford)": ["Fruit & Veg", "Alcohol", "Deli", "Bread", "Fish", "Meat", "Soft Drinks", "Crackers", "Canned Goods", "Pasta/Rice", "Oils", "Toiletries", "Milk", "Cat", "Eggs", "Baking", "Household", "Dairy", "Dips", "Frozen", "Specialty"]
}

FILE_NAME = "shopping_data.json"

# --- 2. DATA PERSISTENCE ---
def load_data():
    if os.path.exists(FILE_NAME):
        try:
            with open(FILE_NAME, "r") as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except: return []
    return []

def save_data():
    try:
        with open(FILE_NAME, "w") as f:
            json.dump(st.session_state.shopping_list, f)
    except:
        st.error("Internal save failed.")

def get_image_html(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as f:
            data_url = base64.b64encode(f.read()).decode("utf-8")
        return f'<img src="data:image/png;base64,{data_url}" width="30">'
    return "🛒"

# --- 3. CALLBACKS ---
def add_item_callback():
    item_val = st.session_state.get("item_input_box", "").strip()
    cat_val = st.session_state.get("item_category_box", "")
    if item_val:
        st.session_state.shopping_list.append({"item": item_val, "category": cat_val, "checked": False})
        save_data()
        st.session_state.item_input_box = ""

# --- 4. APP SETUP ---
st.set_page_config(page_title="NZ Smart Shop", page_icon="🛒")

st.markdown(f"""
    <style>
    .stApp {{ background-color: #f1efea; }}
    footer, header, #MainMenu {{ visibility: hidden; }}
    .section-container {{ display: flex; align-items: center; gap: 10px; margin-top: 25px; margin-bottom: 12px; }}
    .section-title {{ font-size: 24px !important; font-weight: 700; color: #31333F; }}
    .stCheckbox label p {{ font-size: 1.15rem !important; }}
    .stButton button {{ border-radius: 8px; }}
    </style>
""", unsafe_allow_html=True)

if 'shopping_list' not in st.session_state:
    st.session_state.shopping_list = load_data()

# --- 5. STORE SELECT ---
st.markdown(f'<div class="section-container">{get_image_html("Cart.png")}<p class="section-title">Where are you today?</p></div>', unsafe_allow_html=True)
store_choice = st.selectbox("Store Select", list(STORE_LAYOUTS.keys()), label_visibility="collapsed")
current_layout = STORE_LAYOUTS[store_choice]

# --- 6. ADD ITEM ---
with st.expander("➕ Add New Item", expanded=False):
    st.text_input("Item Name", key="item_input_box")
    st.selectbox("Aisle", current_layout, key="item_category_box")
    st.button("Add to List", on_click=add_item_callback, use_container_width=True)

def sort_by_layout(items):
    return sorted(items, key=lambda x: current_layout.index(x['category']) if x['category'] in current_layout else 999)

# --- 7. TODAY ---
st.markdown(f'<div class="section-container">{get_image_html("Today.png")}<p class="section-title">Today</p></div>', unsafe_allow_html=True)
today_items = sort_by_layout([i for i in st.session_state.shopping_list if not i.get('checked', False)])

if not today_items:
    st.info("Basket is empty.")
else:
    for entry in today_items:
        # Checkbox keys need to be unique but also handle symbols/spaces
        c_key = f"t_{entry['item']}_{entry['category']}".replace(" ", "_")
        if st.checkbox(f"**{entry['item']}** — {entry['category']}", key=c_key):
            entry['checked'] = True
            save_data(); st.rerun()

# --- 8. MASTER ---
st.markdown(f'<div class="section-container">{get_image_html("Master.png")}<p class="section-title">Master</p></div>', unsafe_allow_html=True)
col_search, col_edit = st.columns([0.65, 0.35])
with col_search:
    q = st.text_input("Search", placeholder="Type...", label_visibility="collapsed").lower()
with col_edit:
    edit_mode = st.toggle("Edit")

all_master = [i for i in st.session_state.shopping_list if i.get('checked', False)]
master_items = [i for i in all_master if not q or q in i['item'].lower()]
master_items = sort_by_layout(master_items)

if not master_items:
    st.caption("No history.")
else:
    for entry in master_items:
        label = f"**{entry['item']}** — {entry['category']}"
        m_key = f"m_{entry['item']}_{entry['category']}".replace(" ", "_")
        if edit_mode:
            c_item, c_del = st.columns([0.85, 0.15])
            with c_item:
                if not st.checkbox(label, value=True, key=f"ed_{m_key}"):
                    entry['checked'] = False
                    save_data(); st.rerun()
            with c_del:
                if st.button("❌", key=f"del_{m_key}", use_container_width=True):
                    st.session_state.shopping_list = [i for i in st.session_state.shopping_list if i != entry]
                    save_data(); st.rerun()
        else:
            if not st.checkbox(label, value=True, key=f"vw_{m_key}"):
                entry['checked'] = False
                save_data(); st.rerun()

# --- 9. BACKUP / RESTORE TOOLS ---
st.divider()
with st.expander("🛠️ Backup & Restore"):
    # REVISED RESTORE: More robust error handling
    uploaded_file = st.file_uploader("Upload Backup (.json)", type="json")
    if uploaded_file:
        try:
            new_data = json.load(uploaded_file)
            if isinstance(new_data, list):
                st.session_state.shopping_list = new_data
                save_data()
                st.success("List Restored!")
                st.button("Click to Refresh App", on_click=lambda: None) 
            else:
                st.error("File format incorrect.")
        except Exception as e:
            st.error(f"Error reading file: {e}")

    # DOWNLOAD: Indented JSON is easier for the app to read back
    backup_str = json.dumps(st.session_state.shopping_list, indent=2)
    st.download_button(
        label="💾 Save Backup to Phone",
        data=backup_str,
        file_name=f"shop_list_{datetime.now().strftime('%m%d')}.json",
        mime="application/json",
        use_container_width=True
    )

    if st.button("🗑️ Reset Everything", use_container_width=True):
        st.session_state.shopping_list = []
        save_data(); st.rerun()

# --- 10. HOME BUTTON (Escape Hatch) ---
st.button("🏠 Refresh App", use_container_width=True)
