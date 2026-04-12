import streamlit as st
import json
import os
import base64
import uuid # Added for unique IDs
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
                # Ensure every item has a unique ID (for older backups)
                if isinstance(data, list):
                    for item in data:
                        if "id" not in item:
                            item["id"] = str(uuid.uuid4())[:8]
                    return data
        except: pass
    return []

def save_data():
    try:
        with open(FILE_NAME, "w") as f:
            json.dump(st.session_state.shopping_list, f, indent=2)
    except:
        st.error("Save failed.")

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
        # Assign a unique ID immediately
        new_item = {
            "id": str(uuid.uuid4())[:8], 
            "item": item_val, 
            "category": cat_val, 
            "checked": False
        }
        st.session_state.shopping_list.append(new_item)
        save_data()
        st.session_state.item_input_box = ""

# --- 4. SETUP ---
st.set_page_config(page_title="NZ Smart Shop", page_icon="🛒")
st.markdown("""<style>
    .stApp { background-color: #f1efea; }
    footer, header, #MainMenu { visibility: hidden; }
    .section-container { display: flex; align-items: center; gap: 10px; margin-top: 20px; }
    .section-title { font-size: 24px !important; font-weight: 700; color: #31333F; }
    .stButton button { border-radius: 8px; }
</style>""", unsafe_allow_html=True)

if 'shopping_list' not in st.session_state:
    st.session_state.shopping_list = load_data()

# --- 5. STORE & ADD ---
st.markdown(f'<div class="section-container">{get_image_html("Cart.png")}<p class="section-title">Store Select</p></div>', unsafe_allow_html=True)
store_choice = st.selectbox("Store", list(STORE_LAYOUTS.keys()), label_visibility="collapsed")
current_layout = STORE_LAYOUTS[store_choice]

with st.expander("➕ Add New Item"):
    st.text_input("Item Name", key="item_input_box")
    st.selectbox("Aisle", current_layout, key="item_category_box")
    st.button("Add to List", on_click=add_item_callback, use_container_width=True)

def sort_by_layout(items):
    return sorted(items, key=lambda x: current_layout.index(x['category']) if x['category'] in current_layout else 999)

# --- 6. TODAY LIST ---
st.markdown(f'<div class="section-container">{get_image_html("Today.png")}<p class="section-title">Today</p></div>', unsafe_allow_html=True)
today_items = sort_by_layout([i for i in st.session_state.shopping_list if not i.get('checked', False)])

if not today_items:
    st.info("Basket is empty.")
else:
    for entry in today_items:
        # Use the unique ID for the key to prevent crashes
        if st.checkbox(f"**{entry['item']}** — {entry['category']}", key=f"t_{entry['id']}"):
            entry['checked'] = True
            save_data(); st.rerun()

# --- 7. MASTER LIST ---
st.markdown(f'<div class="section-container">{get_image_html("Master.png")}<p class="section-title">Master</p></div>', unsafe_allow_html=True)
col_q, col_ed = st.columns([0.7, 0.3])
with col_q:
    q = st.text_input("Search Master", placeholder="Search...", label_visibility="collapsed").lower()
with col_ed:
    edit_mode = st.toggle("Edit")

master_items = [i for i in st.session_state.shopping_list if i.get('checked', False)]
if q:
    master_items = [i for i in master_items if q in i['item'].lower()]
master_items = sort_by_layout(master_items)

for entry in master_items:
    label = f"**{entry['item']}** — {entry['category']}"
    if edit_mode:
        c1, c2 = st.columns([0.8, 0.2])
        with c1:
            if not st.checkbox(label, value=True, key=f"e_{entry['id']}"):
                entry['checked'] = False
                save_data(); st.rerun()
        with c2:
            if st.button("❌", key=f"d_{entry['id']}"):
                st.session_state.shopping_list = [i for i in st.session_state.shopping_list if i['id'] != entry['id']]
                save_data(); st.rerun()
    else:
        if not st.checkbox(label, value=True, key=f"v_{entry['id']}"):
            entry['checked'] = False
            save_data(); st.rerun()

# --- 8. TOOLS (REVISED RESTORE) ---
st.divider()
with st.expander("🛠️ Backup & Restore"):
    # RESTORE LOGIC
    up = st.file_uploader("Upload Backup (.json)", type="json")
    if up:
        try:
            # 1. Peek at the data first
            new_data = json.load(up)
            if isinstance(new_data, list):
                # 2. Update the local file on the server first
                with open(FILE_NAME, "w") as f:
                    json.dump(new_data, f, indent=2)
                
                # 3. Wipe the current session memory so it's forced to reload
                del st.session_state.shopping_list
                
                st.success("Backup loaded successfully!")
                st.button("Click to Finalize Restore", on_click=lambda: None)
            else:
                st.error("Invalid file format. Must be a list.")
        except Exception as e:
            st.error(f"Error reading backup: {e}")
    
    # DOWNLOAD LOGIC
    st.download_button(
        label="💾 Download Backup", 
        data=json.dumps(st.session_state.shopping_list, indent=2), 
        file_name=f"shop_bak_{datetime.now().strftime('%m%d')}.json", 
        use_container_width=True
    )
    
    if st.button("🗑️ Reset All", use_container_width=True):
        st.session_state.shopping_list = []
        save_data()
        st.rerun()

st.button("🏠 Refresh App", use_container_width=True)
st.button("🏠 Refresh App", use_container_width=True)
