import streamlit as st
import json
import os
import base64

# --- 1. CONFIGURATION ---
STORE_LAYOUTS = {
    "New World (Milford)": [
        "Fruit & Veg", "Fish", "Deli", "Meat", "Specialty", "Eggs", "Bread", "Baking", 
        "Crackers", "Soft Drinks", "Canned Goods", "Pasta/Rice", "Oils", "Toiletries", 
        "Cat", "Household", "Milk", "Dairy", "Dips", "Frozen", "Alcohol",
    ],
    "Pack N Save (Wairau)": [
        "Fruit & Veg", "Fish", "Dairy", "Dips", "Meat", "Deli", "Milk", "Soft Drinks", 
        "Bread", "Eggs", "Toiletries", "Baking", "Crackers", "Canned Goods", 
        "Pasta/Rice", "Oils", "Household", "Cat", "Alcohol", "Frozen", "Specialty", 
    ],
    "Woolworths (Milford)": [
       "Fruit & Veg", "Alcohol", "Deli", "Bread", "Fish", "Meat", "Soft Drinks", 
       "Crackers", "Canned Goods", "Pasta/Rice", "Oils", "Toiletries", "Milk", 
       "Cat", "Eggs", "Baking", "Household", "Dairy", "Dips", "Frozen", "Specialty", 
    ]
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

# Helper to render local PNG icons
def get_image_base64(path):
    with open(path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

# --- 3. APP SETUP & STYLING ---
st.set_page_config(page_title="NZ Smart Shop", page_icon="🛒")

# Custom UI Styling
st.markdown(f"""
    <style>
    /* Background and Content Container */
    .stApp {{
        background-color: #f1efea;
    }}
    
    /* Clean up the mobile header/footer */
    footer, header, #MainMenu {{ visibility: hidden; }}

    /* Section Headers with Icons */
    .section-header {{
        display: flex;
        align-items: center;
        gap: 12px;
        margin-top: 20px;
        margin-bottom: 10px;
    }}
    .section-header img {{
        width: 32px;
        height: 32px;
    }}
    .section-header h2 {{
        margin: 0;
        font-size: 1.8rem;
        color: #31333F;
    }}

    /* Tighten checkbox spacing */
    .stCheckbox label p {{ 
        font-size: 1.1rem !important; 
        margin-bottom: 0px !important; 
        color: #31333F;
    }}
    .stCheckbox {{
        margin-bottom: -12px !important;
    }}
    
    /* Custom button style */
    .stButton button {{
        border-radius: 8px;
        border: 1px solid #d1d1d1;
    }}
    </style>
""", unsafe_allow_html=True)

if 'shopping_list' not in st.session_state:
    st.session_state.shopping_list = load_data()

# --- 4. STORE SELECTION ---
store_choice = st.selectbox("Where are you today?", list(STORE_LAYOUTS.keys()))
current_layout = STORE_LAYOUTS[store_choice]

# --- 5. ADD ITEM SECTION ---
with st.expander("➕ Add New Item", expanded=False):
    new_item = st.text_input("Item Name")
    category = st.selectbox("Aisle", current_layout)
    if st.button("Add to List", use_container_width=True):
        if new_item:
            st.session_state.shopping_list.append({{"item": new_item, "category": category, "checked": False}})
            save_data()
            st.rerun()

# --- 6. SORTING ---
def sort_by_layout(items):
    return sorted(items, key=lambda x: current_layout.index(x['category']) if x['category'] in current_layout else 999)

# --- 7. DISPLAY: TODAY ---
today_icon = get_image_base64("Today.png")
st.markdown(f'''
    <div class="section-header">
        <img src="data:image/png;base64,{today_icon}">
        <h2>Today</h2>
    </div>
''', unsafe_allow_html=True)

today_items = sort_by_layout([i for i in st.session_state.shopping_list if not i['checked']])

if not today_items:
    st.info("Basket is empty.")
else:
    for entry in today_items:
        label = f"**{entry['item']}** — {entry['category']}"
        if st.checkbox(label, value=False, key=f"today_{entry['item']}"):
            entry['checked'] = True
            save_data()
            st.rerun()

# --- 8. DISPLAY: MASTER ---
master_icon = get_image_base64("Master.png")
st.markdown(f'''
    <div class="section-header">
        <img src="data:image/png;base64,{master_icon}">
        <h2>Master</h2>
    </div>
''', unsafe_allow_html=True)

# Search and Edit Layout
col_search, col_edit = st.columns([0.65, 0.35])
with col_search:
    search_query = st.text_input("Search", placeholder="Type...", label_visibility="collapsed").lower()
with col_edit:
    edit_mode = st.toggle("Edit Mode")

all_master = [i for i in st.session_state.shopping_list if i['checked']]
if search_query:
    master_items = [i for i in all_master if search_query in i['item'].lower() or search_query in i['category'].lower()]
else:
    master_items = all_master

master_items = sort_by_layout(master_items)

if not master_items:
    st.caption("No items found.")
else:
    for entry in master_items:
        label = f"**{entry['item']}** — {entry['category']}"
        
        if edit_mode:
            c_item, c_del = st.columns([0.85, 0.15])
            with c_item:
                if not st.checkbox(label, value=True, key=f"m_edit_{entry['item']}"):
                    entry['checked'] = False
                    save_data(); st.rerun()
            with c_del:
                if st.button("❌", key=f"m_del_{entry['item']}", use_container_width=True):
                    st.session_state.shopping_list = [i for i in st.session_state.shopping_list if i != entry]
                    save_data(); st.rerun()
        else:
            if not st.checkbox(label, value=True, key=f"m_view_{entry['item']}"):
                entry['checked'] = False
                save_data(); st.rerun()

# --- 9. CLEAR ALL ---
if st.session_state.shopping_list:
    st.divider()
    if st.button("🗑️ Clear Everything", use_container_width=True):
        st.session_state.shopping_list = []
        save_data()
        st.rerun()
