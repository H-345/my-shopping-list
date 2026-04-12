import streamlit as st
import json
import os
import base64
import uuid
from datetime import datetime

# --- 1. CONFIGURATION ---
STORE_LAYOUTS = {
    "New World (Milford)": ["Fruit & Veg", "Fish", "Deli", "Bakery", "Meat", "Specialty", "Eggs", "Bread", "Baking", "Crackers", "Chips", "Soft Drinks", "Nuts", "Canned Goods", "Pasta/Rice", "Sauces", "Oils", "Toiletries", "Cat", "Household", "Milk", "Dairy", "Dips", "Frozen", "Alcohol"],
    "Pack N Save (Wairau)": ["Fruit & Veg", "Fish", "Dairy", "Dips", "Meat", "Deli", "Bakery", "Milk", "Soft Drinks", "Bread", "Eggs", "Toiletries", "Baking", "Crackers", "Canned Goods", "Pasta/Rice", "Sauces", "Oils", "Household", "Cat", "Chips", "Nuts", "Alcohol", "Frozen", "Specialty"],
    "Woolworths (Milford)": ["Fruit & Veg", "Alcohol", "Bakery", "Deli", "Nuts", "Bread", "Fish", "Meat", "Soft Drinks", "Chips", "Crackers", "Canned Goods", "Pasta/Rice", "Sauces", "Oils", "Toiletries", "Milk", "Cat", "Eggs", "Baking", "Household", "Dairy", "Dips", "Frozen", "Specialty"]
}

FILE_NAME = "shopping_data.json"

# --- 2. DATA PERSISTENCE ---
def load_data():
    if os.path.exists(FILE_NAME):
        try:
            with open(FILE_NAME, "r") as f:
                data = json.load(f)
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
        pass

def get_image_html(image_path):
    if os.path.exists(image_path):
        try:
            with open(image_path, "rb") as f:
                data_url = base64.b64encode(f.read()).decode("utf-8")
            return f'<img src="data:image/png;base64,{data_url}" width="30">'
        except: pass
    return "🛒"

# --- 3. CALLBACKS ---
def add_item_callback():
    item_val = st.session_state.get("item_input_box", "").strip()
    cat_val = st.session_state.get("item_category_box", "")
    if item_val:
        new_item = {"id": str(uuid.uuid4())[:8], "item": item_val, "category": cat_val, "checked": False}
        st.session_state.shopping_list.append(new_item)
        save_data()
        st.session_state.item_input_box = ""

def force_reload():
    # Only clear the shopping list so it fetches fresh from the file, don't wipe the whole state
    if 'shopping_list' in st.session_state:
        del st.session_state.shopping_list
    st.toast("App Reset & Reloaded")

# --- 4. APP SETUP & STYLING ---
st.set_page_config(page_title="NZ Smart Shop", page_icon="🛒")
st.markdown("""<style>
    .stApp { background-color: #f1efea; }
    footer, header, #MainMenu { visibility: hidden; }
    .section-container { display: flex; align-items: center; gap: 10px; margin-top: 25px; margin-bottom: 12px; }
    .section-title { font-size: 24px !important; font-weight: 700; color: #31333F; margin: 0; }
    .stCheckbox label p { font-size: 1.15rem !important; }
    .stButton button { border-radius: 8px; }
</style>""", unsafe_allow_html=True)

if 'shopping_list' not in st.session_state:
    st.session_state.shopping_list = load_data()

# --- 5. STORE SELECTION ---
st.markdown(f'<div class="section-container">{get_image_html("Cart.png")}<p class="section-title">Store Select</p></div>', unsafe_allow_html=True)
store_choice = st.selectbox("Store", list(STORE_LAYOUTS.keys()), label_visibility="collapsed")
current_layout = STORE_LAYOUTS[store_choice]

# --- 6. ADD ITEM ---
with st.expander("➕ Add New Item"):
    st.text_input("Item Name", key="item_input_box")
    st.selectbox("Aisle", current_layout, key="item_category_box")
    st.button("Add to List", on_click=add_item_callback, use_container_width=True)

def sort_by_layout(items):
    return sorted(items, key=lambda x: current_layout.index(x['category']) if x['category'] in current_layout else 999)

# --- 7. DISPLAY: TODAY ---
st.markdown(f'<div class="section-container">{get_image_html("Today.png")}<p class="section-title">Today</p></div>', unsafe_allow_html=True)
today_raw = [i for i in st.session_state.shopping_list if not i.get('checked', False)]
today_sorted = sort_by_layout(today_raw)

if not today_sorted:
    st.info("Basket is empty.")
else:
    for entry in today_sorted:
        if st.checkbox(f"**{entry['item']}** — {entry['category']}", key=f"t_chk_{entry['id']}", value=False):
            entry['checked'] = True
            save_data()
            st.rerun()

# --- 8. DISPLAY: MASTER ---
st.markdown(f'<div class="section-container">{get_image_html("Master.png")}<p class="section-title">Master</p></div>', unsafe_allow_html=True)
col_search, col_edit = st.columns([0.65, 0.35])
with col_search:
    q = st.text_input("Search", placeholder="Type...", label_visibility="collapsed", key="m_search_input").lower()
with col_edit:
    edit_mode = st.toggle("Edit Mode")

master_raw = [i for i in st.session_state.shopping_list if i.get('checked', False)]
if q: 
    master_raw = [i for i in master_raw if q in i['item'].lower()]
master_sorted = sort_by_layout(master_raw)

if not master_sorted:
    st.caption("No history found.")
else:
    for entry in master_sorted:
        label = f"**{entry['item']}** — {entry['category']}"
        if edit_mode:
            c1, c2 = st.columns([0.85, 0.15])
            with c1:
                if not st.checkbox(label, value=True, key=f"me_chk_{entry['id']}"):
                    entry['checked'] = False
                    save_data(); st.rerun()
            with c2:
                if st.button("❌", key=f"del_btn_{entry['id']}", use_container_width=True):
                    st.session_state.shopping_list = [i for i in st.session_state.shopping_list if i['id'] != entry['id']]
                    save_data(); st.rerun()
        else:
            if not st.checkbox(label, value=True, key=f"mv_chk_{entry['id']}"):
                entry['checked'] = False
                save_data(); st.rerun()

# --- 9. TOOLS: BACKUP & RESTORE ---
st.divider()
with st.expander("🛠️ Backup & Restore"):
    up = st.file_uploader("Upload Backup (.json)", type="json")
    
    # THE FIX: Require a button click to actually process the file
    if up is not None:
        if st.button("🚨 Confirm Restore (Overwrites Current)", use_container_width=True):
            try:
                # getvalue() reads the file safely without breaking on subsequent reruns
                raw_bytes = up.getvalue()
                imported_data = json.loads(raw_bytes)
                
                if isinstance(imported_data, list):
                    st.session_state.shopping_list = imported_data
                    save_data()
                    
                    # Targeted scrub: Only delete the old checkbox memory, leave the store selectors alone
                    for key in list(st.session_state.keys()):
                        if key.startswith(('t_chk_', 'me_chk_', 'mv_chk_')):
                            del st.session_state[key]
                            
                    st.success("✅ Restored! You can now click the 'X' on the file uploader to clear it.")
                    st.rerun()
                else:
                    st.error("Invalid format.")
            except Exception as e:
                st.error(f"Read Error: {e}")

    # Prepared JSON string for download
    try:
        current_data_str = json.dumps(st.session_state.get('shopping_list', []), indent=2)
    except:
        current_data_str = "[]"

    st.download_button("💾 Save Backup to Phone", data=current_data_str, 
                       file_name=f"shop_bak_{datetime.now().strftime('%m%d')}.json", 
                       mime="application/json", use_container_width=True)

    if st.button("🗑️ Reset Everything", use_container_width=True):
        st.session_state.shopping_list = []
        save_data(); st.rerun()

# --- 10. HARD REFRESH ---
st.button("🏠 Refresh App", on_click=force_reload, use_container_width=True)
