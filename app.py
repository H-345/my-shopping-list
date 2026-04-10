import streamlit as st
import json
import os

# --- 1. CONFIGURATION: STORE LAYOUTS ---
# Changed "Cat Food" to "Cat" in all lists
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
        except:
            return []
    return []

def save_data():
    with open(FILE_NAME, "w") as f:
        json.dump(st.session_state.shopping_list, f)

# --- 3. APP SETUP & PWA STYLING ---
st.set_page_config(page_title="NZ Smart Shop", page_icon="🛒")

# Custom CSS for Native App Feel
st.markdown("""
    <style>
    /* Prevents unwanted zooming and text selection */
    html, body, [class*="css"] {
        -webkit-user-select: none; 
        user-select: none;
    }
    
    /* Allow selection only for typing items */
    input {
        -webkit-user-select: text !important;
        user-select: text !important;
    }

    /* Tighter checkbox spacing for mobile */
    .stCheckbox {
        margin-bottom: -10px;
        margin-top: 5px;
    }

    /* Hide Streamlit branding for PWA look */
    footer {visibility: hidden;}
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}

    /* Make buttons look more mobile-friendly */
    .stButton button {
        border-radius: 10px;
        height: 3em;
    }
    </style>
""", unsafe_allow_html=True)

if 'shopping_list' not in st.session_state:
    st.session_state.shopping_list = load_data()

# --- 4. STORE SELECTION ---
store_choice = st.selectbox("Where are you today?", list(STORE_LAYOUTS.keys()))
current_layout = STORE_LAYOUTS[store_choice]

# --- 5. ADD ITEM SECTION ---
with st.expander("➕ Add New Item", expanded=True):
    col1, col2 = st.columns([2, 1])
    new_item = col1.text_input("Item Name")
    category = col2.selectbox("Aisle", current_layout)
    
    if st.button("Add to List", use_container_width=True):
        if new_item:
            st.session_state.shopping_list.append({
                "item": new_item, 
                "category": category, 
                "checked": False
            })
            save_data()
            st.rerun()

# --- 6. SORTING HELPER ---
def sort_by_layout(items):
    return sorted(items, key=lambda x: current_layout.index(x['category']) if x['category'] in current_layout else 999)

# --- 7. DISPLAY: TODAY ---
st.header("📍 Today")
today_items = sort_by_layout([i for i in st.session_state.shopping_list if not i['checked']])

if not today_items:
    st.info("Nothing to buy yet!")
else:
    for entry in today_items:
        col_check, col_text = st.columns([0.15, 0.85])
        
        # Checking logic
        if col_check.checkbox("", value=False, key=f"today_{entry['item']}", label_visibility="collapsed"):
            entry['checked'] = True
            save_data()
            st.rerun()
            
        col_text.markdown(f"**{entry['item']}** — {entry['category']}")

# --- 8. DISPLAY: MASTER ---
st.header("🏁 Master")
master_items = sort_by_layout([i for i in st.session_state.shopping_list if i['checked']])

if not master_items:
    st.caption("Checked items will appear here.")
else:
    for entry in master_items:
        col_check, col_text, col_del = st.columns([0.15, 0.70, 0.15])
        
        # Uncheck logic
        if not col_check.checkbox("", value=True, key=f"master_{entry['item']}", label_visibility="collapsed"):
            entry['checked'] = False
            save_data()
            st.rerun()
            
        col_text.markdown(f"~~**{entry['item']}** — {entry['category']}~~")
        
        # Delete item permanently
        if col_del.button("❌", key=f"del_{entry['item']}"):
            st.session_state.shopping_list.remove(entry)
            save_data()
            st.rerun()

# --- 9. CLEAR ALL ---
if st.session_state.shopping_list:
    st.divider()
    if st.button("Clear Everything"):
        st.session_state.shopping_list = []
        save_data()
        st.rerun()
