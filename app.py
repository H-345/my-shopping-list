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
                return json.load(f)
        except: return []
    return []

def save_data():
    with open(FILE_NAME, "w") as f:
        json.dump(st.session_state.shopping_list, f)

def get_image_html(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as f:
            contents = f.read()
        data_url = base64.b64encode(contents).decode("utf-8")
        return f'<img src="data:image/png;base64,{data_url}" width="30">'
    return "🛒"

# --- 3. APP SETUP & STYLING ---
st.set_page_config(page_title="NZ Smart Shop", page_icon="🛒")

st.markdown(f"""
    <style>
    .stApp {{ background-color: #f1efea; }}
    footer, header, #MainMenu {{ visibility: hidden; }}
    .section-container {{ display: flex; align-items: center; gap: 10px; margin-top: 25px; margin-bottom: 12px !important; }}
    .section-title {{ font-size: 24px !important; font-weight: 700; margin: 0 !important; color: #31333F; }}
    [data-testid="stSelectbox"], [data-testid="stTextInput"] {{ margin-top: 0px !important; }}
    .stCheckbox label p {{ font-size: 1.15rem !important; margin-bottom: 0px !important; }}
    .stCheckbox {{ margin-bottom: -12px !important; }}
    .stButton button {{ border-radius: 8px; }}
    
    /* Style for the backup link to make it look like a nice button */
    .download-btn {{
        display: inline-block;
        padding: 0.5em 1em;
        color: #31333F;
        background-color: #fff;
        border: 1px solid #d1d1d1;
        border-radius: 8px;
        text-decoration: none;
        text-align: center;
        width: 100%;
    }}
    </style>
""", unsafe_allow_html=True)

if 'shopping_list' not in st.session_state:
    st.session_state.shopping_list = load_data()

# --- 4. STORE SELECTION ---
st.markdown(f'''<div class="section-container">{get_image_html("Cart.png")}<p class="section-title">Where are you today?</p></div>''', unsafe_allow_html=True)
store_choice = st.selectbox("Store Select", list(STORE_LAYOUTS.keys()), label_visibility="collapsed")
current_layout = STORE_LAYOUTS[store_choice]

# --- 5. ADD ITEM ---
with st.expander("➕ Add New Item", expanded=False):
    new_item = st.text_input("Item Name", key="input_reset")
    category = st.selectbox("Aisle", current_layout)
    if st.button("Add to List", use_container_width=True):
        if new_item:
            st.session_state.shopping_list.append({"item": new_item, "category": category, "checked": False})
            save_data()
            st.session_state.input_reset = ""
            st.rerun()

def sort_by_layout(items):
    return sorted(items, key=lambda x: current_layout.index(x['category']) if x['category'] in current_layout else 999)

# --- 6. DISPLAY: TODAY ---
st.markdown(f'''<div class="section-container">{get_image_html("Today.png")}<p class="section-title">Today</p></div>''', unsafe_allow_html=True)
today_items = sort_by_layout([i for i in st.session_state.shopping_list if not i.get('checked', False)])

if not today_items:
    st.info("Basket is empty.")
else:
    for entry in today_items:
        label = f"**{entry['item']}** — {entry['category']}"
        if st.checkbox(label, value=False, key=f"today_{entry['item']}"):
            entry['checked'] = True
            save_data(); st.rerun()

# --- 7. DISPLAY: MASTER ---
st.markdown(f'''<div class="section-container">{get_image_html("Master.png")}<p class="section-title">Master</p></div>''', unsafe_allow_html=True)
col_search, col_edit = st.columns([0.65, 0.35])
with col_search:
    search_query = st.text_input("Search", placeholder="Type...", label_visibility="collapsed").lower()
with col_edit:
    edit_mode = st.toggle("Edit")

all_master = [i for i in st.session_state.shopping_list if i.get('checked', False)]
master_items = [i for i in all_master if not search_query or search_query in i['item'].lower()]
master_items = sort_by_layout(master_items)

if not master_items:
    st.caption("No history.")
else:
    for entry in master_items:
        label = f"**{entry['item']}** — {entry['category']}"
        if edit_mode:
            c_item, c_del = st.columns([0.85, 0.15])
            with c_item:
                if not st.checkbox(label, value=True, key=f"me_{entry['item']}"):
                    entry['checked'] = False
                    save_data(); st.rerun()
            with c_del:
                if st.button("❌", key=f"md_{entry['item']}", use_container_width=True):
                    st.session_state.shopping_list = [i for i in st.session_state.shopping_list if i != entry]
                    save_data(); st.rerun()
        else:
            if not st.checkbox(label, value=True, key=f"mv_{entry['item']}"):
                entry['checked'] = False
                save_data(); st.rerun()

# --- 8. UTILITIES: BACKUP & RESTORE ---
st.divider()

# Restoration Logic
with st.expander("🛠️ App Tools (Backup & Restore)"):
    # Restore Button
    uploaded_file = st.file_uploader("Restore List from Phone Backup", type="json")
    if uploaded_file is not None:
        st.session_state.shopping_list = json.load(uploaded_file)
        save_data()
        st.success("List Restored!")
        st.rerun()

    # Manual Download (Always available)
    json_data = json.dumps(st.session_state.shopping_list)
    st.download_button(
        label="💾 Download Manual Backup",
        data=json_data,
        file_name=f"shopping_backup_{datetime.now().strftime('%Y%m%d')}.json",
        mime="application/json",
        use_container_width=True
    )

    if st.button("🗑️ Reset All Data", use_container_width=True):
        st.session_state.shopping_list = []
        save_data(); st.rerun()
