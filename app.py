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

# --- 3. APP SETUP & SELECTIVE CSS ---
st.set_page_config(page_title="NZ Smart Shop", page_icon="🛒")

st.markdown("""
    <style>
    /* Global Cleanliness */
    * { -webkit-user-select: none; user-select: none; }
    input { -webkit-user-select: text !important; user-select: text !important; }
    footer, header, #MainMenu { visibility: hidden; }

    /* ONLY apply horizontal force to the shopping rows (Today/Master) */
    /* This prevents the "Add New Item" section from squishing */
    .shopping-row [data-testid="stHorizontalBlock"] {
        flex-wrap: nowrap !important;
        align-items: center !important;
    }

    .shopping-row [data-testid="column"] {
        min-width: 0 !important;
    }

    /* Checkbox text size */
    .stCheckbox label p { font-size: 1.1rem !important; }

    /* Delete button styling */
    .stButton button { padding: 0 !important; height: 2.5em; border-radius: 8px; }
    </style>
""", unsafe_allow_html=True)

if 'shopping_list' not in st.session_state:
    st.session_state.shopping_list = load_data()

# --- 4. STORE SELECTION ---
store_choice = st.selectbox("Where are you today?", list(STORE_LAYOUTS.keys()))
current_layout = STORE_LAYOUTS[store_choice]

# --- 5. ADD ITEM SECTION (FIXED: NOW STACKS) ---
with st.expander("➕ Add New Item", expanded=False):
    # Standard columns here will stack on mobile because they aren't wrapped in 'shopping-row'
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
    # Wrapping rows in a div with class 'shopping-row' to trigger the CSS fix
    st.markdown('<div class="shopping-row">', unsafe_allow_html=True)
    for entry in today_items:
        label = f"**{entry['item']}** — {entry['category']}"
        if st.checkbox(label, value=False, key=f"today_{entry['item']}"):
            entry['checked'] = True
            save_data()
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# --- 8. DISPLAY: MASTER ---
st.header("🏁 Master")
search_query = st.text_input("🔍 Search Master List", placeholder="Type...").lower()

# Get master items and filter them
all_master = [i for i in st.session_state.shopping_list if i['checked']]
if search_query:
    master_items = [i for i in all_master if search_query in i['item'].lower() or search_query in i['category'].lower()]
else:
    master_items = all_master

master_items = sort_by_layout(master_items)

if not master_items:
    st.caption("No items found.")
else:
    st.markdown('<div class="shopping-row">', unsafe_allow_html=True)
    for entry in master_items:
        col_item, col_del = st.columns([0.85, 0.15])
        
        with col_item:
            label = f"~~**{entry['item']}** — {entry['category']}~~"
            # Using a safer toggle logic to prevent state errors
            if not st.checkbox(label, value=True, key=f"master_check_{entry['item']}"):
                entry['checked'] = False
                save_data()
                st.rerun()
                
        with col_del:
            if st.button("❌", key=f"del_btn_{entry['item']}", use_container_width=True):
                # Safer removal using list comprehension to avoid mutation errors
                st.session_state.shopping_list = [i for i in st.session_state.shopping_list if i != entry]
                save_data()
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# --- 9. CLEAR ALL ---
if st.session_state.shopping_list:
    st.divider()
    if st.button("Clear Everything"):
        st.session_state.shopping_list = []
        save_data()
        st.rerun()
