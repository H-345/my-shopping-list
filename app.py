import streamlit as st
import json
import os

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

# --- 3. APP SETUP & CSS ---
st.set_page_config(page_title="NZ Smart Shop", page_icon="🛒")

st.markdown("""
    <style>
    /* Global Cleanliness */
    * { -webkit-user-select: none; user-select: none; }
    input { -webkit-user-select: text !important; user-select: text !important; }
    footer, header, #MainMenu { visibility: hidden; }

    /* ABSOLUTE FORCE: Keep Master Row horizontal */
    .master-row [data-testid="stHorizontalBlock"] {
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        align-items: center !important;
        gap: 0px !important;
    }
    
    /* Column 1 (Checkbox): Takes up remaining space */
    .master-row [data-testid="column"]:nth-of-type(1) {
        flex: 1 1 auto !important;
        width: auto !important;
        min-width: 0 !important;
    }

    /* Column 2 (Delete Button): Locked to exactly 35px */
    .master-row [data-testid="column"]:nth-of-type(2) {
        flex: 0 0 35px !important;
        width: 35px !important;
        min-width: 35px !important;
        padding-left: 5px !important;
    }

    /* The 'X' Button: Make it much smaller */
    .master-row button {
        width: 24px !important;
        height: 24px !important;
        min-height: 24px !important;
        padding: 0 !important;
        font-size: 12px !important;
        border-radius: 4px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }

    /* Checkbox spacing */
    .stCheckbox label p { 
        font-size: 1.1rem !important; 
        margin-bottom: 0px !important; 
    }
    .stCheckbox {
        margin-bottom: -10px !important;
    }
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
            st.session_state.shopping_list.append({"item": new_item, "category": category, "checked": False})
            save_data()
            st.rerun()

# --- 6. SORTING ---
def sort_by_layout(items):
    return sorted(items, key=lambda x: current_layout.index(x['category']) if x['category'] in current_layout else 999)

# --- 7. DISPLAY: TODAY ---
st.header("📍 Today")
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
st.header("🏁 Master")
search_query = st.text_input("🔍 Search Master List", placeholder="Type...").lower()

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
        st.markdown('<div class="master-row">', unsafe_allow_html=True)
        # The CSS above now strictly controls the width of these columns,
        # so the ratio we pass here is mostly ignored.
        c_item, c_del = st.columns([0.85, 0.15])
        
        with c_item:
            label = f"**{entry['item']}** — {entry['category']}"
            if not st.checkbox(label, value=True, key=f"m_chk_{entry['item']}"):
                entry['checked'] = False
                save_data(); st.rerun()
                
        with c_del:
            if st.button("❌", key=f"m_del_{entry['item']}"):
                st.session_state.shopping_list = [i for i in st.session_state.shopping_list if i != entry]
                save_data(); st.rerun()
                
        st.markdown('</div>', unsafe_allow_html=True)

# --- 9. CLEAR ALL ---
if st.session_state.shopping_list:
    st.divider()
    if st.button("🗑️ Clear Everything", use_container_width=True):
        st.session_state.shopping_list = []
        save_data()
        st.rerun()
