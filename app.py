import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import os
import base64

# --- 1. CONFIGURATION ---
STORE_LAYOUTS = {
    "New World (Milford)": ["Fruit & Veg", "Fish", "Deli", "Meat", "Specialty", "Eggs", "Bread", "Baking", "Crackers", "Soft Drinks", "Canned Goods", "Pasta/Rice", "Oils", "Toiletries", "Cat", "Household", "Milk", "Dairy", "Dips", "Frozen", "Alcohol"],
    "Pack N Save (Wairau)": ["Fruit & Veg", "Fish", "Dairy", "Dips", "Meat", "Deli", "Milk", "Soft Drinks", "Bread", "Eggs", "Toiletries", "Baking", "Crackers", "Canned Goods", "Pasta/Rice", "Oils", "Household", "Cat", "Alcohol", "Frozen", "Specialty"],
    "Woolworths (Milford)": ["Fruit & Veg", "Alcohol", "Deli", "Bread", "Fish", "Meat", "Soft Drinks", "Crackers", "Canned Goods", "Pasta/Rice", "Oils", "Toiletries", "Milk", "Cat", "Eggs", "Baking", "Household", "Dairy", "Dips", "Frozen", "Specialty"]
}

# --- 2. GOOGLE SHEETS CONNECTION ---
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    try:
        # ttl=0 ensures we don't use old cached data
        df = conn.read(ttl=0)
        if df.empty:
            return []
        # Ensure 'checked' column exists and is boolean
        if 'checked' not in df.columns:
            df['checked'] = False
        # Fill empty checkmarks with False
        df['checked'] = df['checked'].fillna(False).astype(bool)
        return df.to_dict('records')
    except Exception as e:
        # If the sheet is totally new/blank, return empty list instead of crashing
        return []

def save_to_sheet(data_list):
    if not data_list:
        # Create a blank structure with headers if list is wiped
        df = pd.DataFrame(columns=["item", "category", "checked"])
    else:
        df = pd.DataFrame(data_list)
    
    # Crucial: Ensure the column names are exactly what we expect
    df = df[["item", "category", "checked"]]
    conn.update(data=df)

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
    </style>
""", unsafe_allow_html=True)

# LOAD DATA
if 'shopping_list' not in st.session_state:
    st.session_state.shopping_list = load_data()

# --- 4. STORE SELECTION ---
st.markdown(f'''<div class="section-container">{get_image_html("Cart.png")}<p class="section-title">Where are you today?</p></div>''', unsafe_allow_html=True)
store_choice = st.selectbox("Store Select", list(STORE_LAYOUTS.keys()), label_visibility="collapsed")
current_layout = STORE_LAYOUTS[store_choice]

# --- 5. ADD ITEM ---
with st.expander("➕ Add New Item", expanded=False):
    new_item = st.text_input("Item Name", key="new_item_box")
    category = st.selectbox("Aisle", current_layout)
    if st.button("Add to List", use_container_width=True):
        if new_item:
            st.session_state.shopping_list.append({"item": new_item, "category": category, "checked": False})
            save_to_sheet(st.session_state.shopping_list)
            st.session_state.new_item_box = "" # Reset box
            st.rerun()

def sort_by_layout(items):
    return sorted(items, key=lambda x: current_layout.index(x['category']) if x['category'] in current_layout else 999)

# --- 7. DISPLAY: TODAY ---
st.markdown(f'''<div class="section-container">{get_image_html("Today.png")}<p class="section-title">Today</p></div>''', unsafe_allow_html=True)
today_items = sort_by_layout([i for i in st.session_state.shopping_list if not i.get('checked', False)])

if not today_items:
    st.info("Basket is empty.")
else:
    for entry in today_items:
        label = f"**{entry['item']}** — {entry['category']}"
        if st.checkbox(label, value=False, key=f"today_{entry['item']}"):
            entry['checked'] = True
            save_to_sheet(st.session_state.shopping_list)
            st.rerun()

# --- 8. DISPLAY: MASTER ---
st.markdown(f'''<div class="section-container">{get_image_html("Master.png")}<p class="section-title">Master</p></div>''', unsafe_allow_html=True)
col_search, col_edit = st.columns([0.65, 0.35])
with col_search:
    search_query = st.text_input("Search", placeholder="Type...", label_visibility="collapsed", key="m_search").lower()
with col_edit:
    edit_mode = st.toggle("Edit")

all_master = [i for i in st.session_state.shopping_list if i.get('checked', False)]
master_items = [i for i in all_master if not search_query or search_query in i['item'].lower() or search_query in i['category'].lower()]
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
                    save_to_sheet(st.session_state.shopping_list); st.rerun()
            with c_del:
                if st.button("❌", key=f"md_{entry['item']}"):
                    st.session_state.shopping_list = [i for i in st.session_state.shopping_list if i != entry]
                    save_to_sheet(st.session_state.shopping_list); st.rerun()
        else:
            if not st.checkbox(label, value=True, key=f"mv_{entry['item']}"):
                entry['checked'] = False
                save_to_sheet(st.session_state.shopping_list); st.rerun()

# --- 9. CLEAR ALL ---
if st.session_state.shopping_list:
    st.divider()
    if st.button("🗑️ Clear Everything", use_container_width=True):
        st.session_state.shopping_list = []
        save_to_sheet([])
        st.rerun()
