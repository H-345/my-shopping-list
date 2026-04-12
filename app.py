import streamlit as st
import json
import os
import base64
import uuid
from datetime import datetime

# --- 1. CONFIGURATION ---
STORE_LAYOUTS = {
    "New World (Milford)": ["Fruit & Veg", "Fish", "Deli", "Meat", "Specialty", "Eggs", "Bread", "Baking", "Crackers", "Soft Drinks", "Canned Goods", "Pasta/Rice", "Oils", "Toiletries", "Cat", "Household", "Milk", "Dairy", "Dips", "Frozen", "Alcohol"],
    "Pack N Save (Wairau)": ["Fruit & Veg", "Fish", "Dairy", "Dips", "Meat", "Deli", "Milk", "Soft Drinks", "Bread", "Eggs", "Toiletries", "Baking", "Crackers", "Canned Goods", "Pasta/Rice", "Oils", "Household", "Cat", "Alcohol", "Frozen", "Specialty"],
    "Woolworths (Milford)": ["Fruit & Veg", "Alcohol", "Deli", "Bread", "Fish", "Meat", "Soft Drinks", "Crackers", "Canned Goods", "Pasta/Rice", "Oils", "Toiletries", "Milk", "Cat", "Eggs", "Baking", "Household", "Dairy", "Dips", "Frozen", "Specialty"]
}

FILE_NAME = "shopping_data.json"

# --- 2. DATA PERSISTENCE ---
def save_data():
    """Safely write to the local file."""
    try:
        with open(FILE_NAME, "w") as f:
            json.dump(st.session_state.shopping_list, f)
    except Exception as e:
        st.sidebar.error(f"Save failed: {e}")

def load_data():
    """Load existing data or return an empty list."""
    if os.path.exists(FILE_NAME):
        try:
            with open(FILE_NAME, "r") as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except:
            return []
    return []

def get_image_html(image_path):
    """Convert local icons to HTML for the headers."""
    if os.path.exists(image_path):
        try:
            with open(image_path, "rb") as f:
                data_url = base64.b64encode(f.read()).decode("utf-8")
            return f'<img src="data:image/png;base64,{data_url}" width="30">'
        except: pass
    return "🛒"

# --- 3. APP SETUP & STYLING ---
st.set_page_config(page_title="NZ Smart Shop", page_icon="🛒")

st.markdown(f"""
    <style>
    .stApp {{ background-color: #f1efea; }}
    footer, header, #MainMenu {{ visibility: hidden; }}
    .section-container {{ display: flex; align-items: center; gap: 10px; margin-top: 20px; margin-bottom: 12px; }}
    .section-title {{ font-size: 24px !important; font-weight: 700; margin: 0 !important; color: #31333F; }}
    [data-testid="stForm"] {{ border: none; padding: 0; }}
    .stCheckbox label p {{ font-size: 1.15rem !important; margin-bottom: 0px !important; }}
    .stCheckbox {{ margin-bottom: -12px !important; }}
    .stButton button {{ border-radius: 8px; }}
    </style>
""", unsafe_allow_html=True)

# Always initialize session state first
if 'shopping_list' not in st.session_state:
    st.session_state.shopping_list = load_data()

# Sorting Helper
def sort_items(items, layout):
    return sorted(items, key=lambda x: layout.index(x['category']) if x['category'] in layout else 999)

# --- 4. STORE SELECTION ---
st.markdown(f'<div class="section-container">{get_image_html("Cart.png")}<p class="section-title">Where are you today?</p></div>', unsafe_allow_html=True)
store_choice = st.selectbox("Store Select", list(STORE_LAYOUTS.keys()), label_visibility="collapsed")
current_layout = STORE_LAYOUTS[store_choice]

# --- 5. ADD ITEM SECTION (USING ST.FORM FOR STABILITY) ---
with st.expander("➕ Add New Item", expanded=False):
    with st.form("add_item_form", clear_on_submit=True):
        name = st.text_input("Item Name")
        cat = st.selectbox("Aisle", current_layout)
        submit = st.form_submit_button("Add to List", use_container_width=True)
        
        if submit and name:
            new_entry = {
                "id": str(uuid.uuid4()), 
                "item": name.strip(), 
                "category": cat, 
                "checked": False
            }
            st.session_state.shopping_list.append(new_entry)
            save_data()
            st.rerun()

# --- 6. DISPLAY: TODAY ---
st.markdown(f'<div class="section-container">{get_image_html("Today.png")}<p class="section-title">Today</p></div>', unsafe_allow_html=True)

# Filter items for Today (not checked)
today_list = [i for i in st.session_state.shopping_list if not i.get('checked', False)]
today_list = sort_items(today_list, current_layout)

if not today_list:
    st.info("Basket is empty.")
else:
    for entry in today_list:
        # We use the unique UUID for the key
        if st.checkbox(f"**{entry['item']}** — {entry['category']}", key=f"today_{entry['id']}"):
            entry['checked'] = True
            save_data()
            st.rerun()

# --- 7. DISPLAY: MASTER ---
st.markdown(f'<div class="section-container">{get_image_html("Master.png")}<p class="section-title">Master</p></div>', unsafe_allow_html=True)
col_q, col_ed = st.columns([0.7, 0.3])
with col_q:
    search = st.text_input("Search", placeholder="Search master...", label_visibility="collapsed").lower()
with col_ed:
    edit_mode = st.toggle("Edit")

# Filter items for Master (checked)
master_list = [i for i in st.session_state.shopping_list if i.get('checked', False)]
if search:
    master_list = [i for i in master_list if search in i['item'].lower()]
master_list = sort_items(master_list, current_layout)

if not master_list:
    st.caption("No history items.")
else:
    for entry in master_list:
        label = f"**{entry['item']}** — {entry['category']}"
        if edit_mode:
            c1, c2 = st.columns([0.85, 0.15])
            with c1:
                if not st.checkbox(label, value=True, key=f"edit_{entry['id']}"):
                    entry['checked'] = False
                    save_data(); st.rerun()
            with c2:
                if st.button("❌", key=f"del_{entry['id']}", use_container_width=True):
                    st.session_state.shopping_list = [i for i in st.session_state.shopping_list if i['id'] != entry['id']]
                    save_data(); st.rerun()
        else:
            if not st.checkbox(label, value=True, key=f"view_{entry['id']}"):
                entry['checked'] = False
                save_data(); st.rerun()

# --- 8. UTILITIES ---
st.divider()
with st.expander("🛠️ Backup & Restore"):
    # Restore
    up = st.file_uploader("Restore from Backup (.json)", type="json")
    if up:
        st.session_state.shopping_list = json.load(up)
        save_data(); st.rerun()
    
    # Backup
    backup_str = json.dumps(st.session_state.shopping_list)
    st.download_button("💾 Download Backup to Phone", data=backup_str, file_name=f"shop_backup_{datetime.now().strftime('%m%d')}.json", use_container_width=True)

    if st.button("🗑️ Reset Everything", use_container_width=True):
        st.session_state.shopping_list = []
        save_data(); st.rerun()
