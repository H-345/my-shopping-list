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

# --- 2. DATA UTILITIES ---
def save_data():
    try:
        with open(FILE_NAME, "w") as f:
            json.dump(st.session_state.shopping_list, f)
    except Exception as e:
        st.error(f"Save error: {e}")

def load_data():
    if os.path.exists(FILE_NAME):
        try:
            with open(FILE_NAME, "r") as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except: return []
    return []

def get_image_html(image_path):
    if os.path.exists(image_path):
        try:
            with open(image_path, "rb") as f:
                data_url = base64.b64encode(f.read()).decode("utf-8")
            return f'<img src="data:image/png;base64,{data_url}" width="30">'
        except: pass
    return "🛒"

# --- 3. APP SETUP & CSS ---
st.set_page_config(page_title="NZ Smart Shop", page_icon="🛒")

st.markdown(f"""
    <style>
    .stApp {{ background-color: #f1efea; }}
    footer, header, #MainMenu {{ visibility: hidden; }}
    .section-container {{ display: flex; align-items: center; gap: 10px; margin-top: 20px; margin-bottom: 12px; }}
    .section-title {{ font-size: 24px !important; font-weight: 700; margin: 0 !important; color: #31333F; }}
    [data-testid="stSelectbox"], [data-testid="stTextInput"] {{ margin-top: 0px !important; }}
    .stCheckbox label p {{ font-size: 1.15rem !important; margin-bottom: 0px !important; }}
    .stCheckbox {{ margin-bottom: -12px !important; }}
    .stButton button {{ border-radius: 8px; }}
    </style>
""", unsafe_allow_html=True)

# Initialize Session State
if 'shopping_list' not in st.session_state:
    st.session_state.shopping_list = load_data()

# --- 4. CALLBACK FOR ADDING ITEM ---
def add_item_callback():
    name = st.session_state.new_item_name
    cat = st.session_state.new_item_cat
    if name:
        st.session_state.shopping_list.append({"item": name, "category": cat, "checked": False})
        save_data()
        st.session_state.new_item_name = "" # This clears the text box

# --- 5. STORE SELECTION ---
st.markdown(f'<div class="section-container">{get_image_html("Cart.png")}<p class="section-title">Where are you today?</p></div>', unsafe_allow_html=True)
store_choice = st.selectbox("Store Select", list(STORE_LAYOUTS.keys()), label_visibility="collapsed")
current_layout = STORE_LAYOUTS[store_choice]

# --- 6. ADD ITEM SECTION ---
with st.expander("➕ Add New Item"):
    st.text_input("Item Name", key="new_item_name")
    st.selectbox("Aisle", current_layout, key="new_item_cat")
    st.button("Add to List", on_click=add_item_callback, use_container_width=True)

# Sorting Function
def sort_items(items):
    return sorted(items, key=lambda x: current_layout.index(x['category']) if x['category'] in current_layout else 999)

# --- 7. DISPLAY: TODAY ---
st.markdown(f'<div class="section-container">{get_image_html("Today.png")}<p class="section-title">Today</p></div>', unsafe_allow_html=True)
today = sort_items([i for i in st.session_state.shopping_list if not i.get('checked', False)])

if not today:
    st.info("Basket is empty.")
else:
    for entry in today:
        if st.checkbox(f"**{entry['item']}** — {entry['category']}", key=f"t_{entry['item']}"):
            entry['checked'] = True
            save_data(); st.rerun()

# --- 8. DISPLAY: MASTER ---
st.markdown(f'<div class="section-container">{get_image_html("Master.png")}<p class="section-title">Master</p></div>', unsafe_allow_html=True)
col_search, col_edit = st.columns([0.65, 0.35])
with col_search:
    q = st.text_input("Search", placeholder="Type...", label_visibility="collapsed", key="search").lower()
with col_edit:
    edit_mode = st.toggle("Edit")

master = [i for i in st.session_state.shopping_list if i.get('checked', False)]
filtered = [i for i in master if not q or q in i['item'].lower()]
filtered = sort_items(filtered)

if not filtered:
    st.caption("No history found.")
else:
    for entry in filtered:
        label = f"**{entry['item']}** — {entry['category']}"
        if edit_mode:
            c1, c2 = st.columns([0.85, 0.15])
            with c1:
                if not st.checkbox(label, value=True, key=f"me_{entry['item']}"):
                    entry['checked'] = False
                    save_data(); st.rerun()
            with c2:
                if st.button("❌", key=f"del_{entry['item']}", use_container_width=True):
                    st.session_state.shopping_list = [i for i in st.session_state.shopping_list if i != entry]
                    save_data(); st.rerun()
        else:
            if not st.checkbox(label, value=True, key=f"mv_{entry['item']}"):
                entry['checked'] = False
                save_data(); st.rerun()

# --- 9. BACKUP TOOLS ---
st.divider()
with st.expander("🛠️ Backup & Restore"):
    # Restore
    up = st.file_uploader("Upload Phone Backup (.json)", type="json")
    if up:
        st.session_state.shopping_list = json.load(up)
        save_data(); st.rerun()
    
    # Download
    backup_data = json.dumps(st.session_state.shopping_list)
    st.download_button("💾 Save Backup to Phone", data=backup_data, file_name=f"shop_backup_{datetime.now().strftime('%Y%m%d')}.json", use_container_width=True)

    if st.button("🗑️ Reset All Data", use_container_width=True):
        st.session_state.shopping_list = []
        save_data(); st.rerun()
