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

# --- 3. APP SETUP & CRITICAL CSS ---
st.set_page_config(page_title="NZ Smart Shop", page_icon="🛒")

st.markdown("""
    <style>
    /* PWA Cleanliness */
    * { -webkit-user-select: none; user-select: none; }
    input { -webkit-user-select: text !important; user-select: text !important; }
    footer, header, #MainMenu { visibility: hidden; }
    
    /* Make the checkbox text slightly larger for mobile */
    .stCheckbox label p {
        font-size: 1.1rem !important;
    }
    
    /* MAGIC FIX 2: Stop Streamlit from stacking columns on mobile */
    [data-testid="stHorizontalBlock"] {
        flex-wrap: nowrap !important;
        align-items: center !important; /* Vertically centers the delete button */
    }
    
    /* Removes the mobile rule that forces columns to be 100% wide */
    [data-testid="column"] {
        min-width: 0 !important; 
    }

    /* Tidy up the delete button to fit cleanly */
    .stButton button {
        padding: 0 !important;
        height: 2.5em;
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
    # This will now neatly sit side-by-side on mobile too!
    col1, col2 = st.columns([2, 1], gap="small")
    new_item = col1.text_input("Item Name")
    category = col2.selectbox("Aisle", current_layout)
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
        # Native label markdown - guaranteed perfect spacing
        label = f"**{entry['item']}** — {entry['category']}"
        if st.checkbox(label, value=False, key=f"today_{entry['item']}"):
            entry['checked'] = True
            save_data()
            st.rerun()

# --- 8. DISPLAY: MASTER ---
st.header("🏁 Master")
search_query = st.text_input("🔍 Search Master List", placeholder="Type...").lower()

master_items = sort_by_layout([i for i in st.session_state.shopping_list if i['checked']])
if search_query:
    master_items = [i for i in master_items if search_query in i['item'].lower() or search_query in i['category'].lower()]

if not master_items:
    st.caption("No items found.")
else:
    for entry in master_items:
        # Columns now forced to stay side-by-side by our new CSS
        col_item, col_del = st.columns([0.85, 0.15], gap="small")
        
        with col_item:
            label = f"~~**{entry['item']}** — {entry['category']}~~"
            if not st.checkbox(label, value=True, key=f"master_{entry['item']}"):
                entry['checked'] = False
                save_data()
                st.rerun()
                
        with col_del:
            # Button will perfectly sit inside the 15% column
            if st.button("❌", key=f"del_{entry['item']}", use_container_width=True):
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
