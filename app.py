import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
from pathlib import Path
import hashlib
import psycopg2
from urllib.parse import urlparse

# Page configuration
st.set_page_config(
    page_title="Wedding Guest Addresses",
    page_icon="💒",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #FF6B9D;
        font-size: 3rem;
        margin-bottom: 0.5rem;
        font-weight: bold;
    }
    .sub-header {
        text-align: center;
        color: #666;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    .form-container {
        background-color: #f9f9f9;
        padding: 2rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .success-container {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 10px;
        padding: 2rem;
        text-align: center;
        margin: 2rem 0;
    }
    .error-message {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .admin-login {
        max-width: 400px;
        margin: 0 auto;
        background-color: #f8f9fa;
        padding: 2rem;
        border-radius: 10px;
        border: 1px solid #dee2e6;
    }
    .stSelectbox > div > div > select {
        border-radius: 5px;
    }
    .stTextInput > div > div > input {
        border-radius: 5px;
    }
    .stButton > button {
        background-color: #FF6B9D;
        color: white;
        border-radius: 10px;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: bold;
        transition: all 0.3s;
    }
    .stButton > button:hover {
        background-color: #E55A8A;
        transform: translateY(-2px);
    }
    .metric-container {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #FF6B9D;
    }
</style>
""", unsafe_allow_html=True)

# Get credentials from Streamlit secrets
def get_database_url():
    """Get database URL from Streamlit secrets"""
    try:
        return st.secrets["DATABASE_URL"]
    except KeyError:
        st.error("Missing DATABASE_URL in secrets. Please configure your Supabase database URL.")
        st.stop()

def get_admin_credentials():
    """Get admin credentials from Streamlit secrets"""
    try:
        username = st.secrets["ADMIN_USERNAME"]
        password = st.secrets["ADMIN_PASSWORD"]
        return username, password
    except KeyError as e:
        st.error(f"Missing secret: {e}. Please configure ADMIN_USERNAME and ADMIN_PASSWORD in secrets.")
        st.stop()

# Database connection
def get_db_connection():
    """Get database connection"""
    try:
        database_url = get_database_url()
        return psycopg2.connect(database_url)
    except Exception as e:
        st.error(f"Failed to connect to database: {e}")
        st.stop()

# Initialize database
def init_database():
    """Initialize PostgreSQL database for storing guest addresses"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS guests (
                id SERIAL PRIMARY KEY,
                first_name VARCHAR(100) NOT NULL,
                last_name VARCHAR(100) NOT NULL,
                email VARCHAR(255),
                phone VARCHAR(20),
                address_line1 VARCHAR(255) NOT NULL,
                address_line2 VARCHAR(255),
                city VARCHAR(100) NOT NULL,
                state VARCHAR(10) NOT NULL,
                zip_code VARCHAR(20) NOT NULL,
                country VARCHAR(50) DEFAULT 'USA',
                rsvp_status VARCHAR(20) DEFAULT 'Pending',
                submission_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Fix the sequence to prevent duplicate key errors
        # This ensures the sequence starts from the correct next value
        cursor.execute('''
            SELECT setval('guests_id_seq', COALESCE((SELECT MAX(id) FROM guests), 0), true)
        ''')
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Database initialization failed: {e}")
        return False

def check_admin_credentials(username, password):
    """Check if provided credentials match admin credentials"""
    admin_username, admin_password = get_admin_credentials()
    return username == admin_username and password == admin_password

def is_admin_logged_in():
    """Check if admin is currently logged in"""
    return st.session_state.get('admin_logged_in', False)

def admin_login():
    """Display admin login form"""
    st.markdown('<div class="admin-login">', unsafe_allow_html=True)
    st.subheader("🔐 Admin Login")
    st.write("Please enter admin credentials to access this page.")
    
    with st.form("admin_login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        login_button = st.form_submit_button("Login")
        
        if login_button:
            if check_admin_credentials(username, password):
                st.session_state['admin_logged_in'] = True
                st.success("✅ Login successful!")
                st.rerun()
            else:
                st.error("❌ Invalid credentials. Please try again.")
    
    st.markdown('</div>', unsafe_allow_html=True)

def admin_logout():
    """Logout admin user"""
    st.session_state['admin_logged_in'] = False
    st.rerun()

def save_guest_data(guest_data):
    """Save guest data to PostgreSQL database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO guests (
                first_name, last_name, email, phone, address_line1, address_line2,
                city, state, zip_code, country
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (
            guest_data['first_name'],
            guest_data['last_name'],
            guest_data['email'],
            guest_data['phone'],
            guest_data['address_line1'],
            guest_data['address_line2'],
            guest_data['city'],
            guest_data['state'],
            guest_data['zip_code'],
            guest_data['country']
        ))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Error saving data: {str(e)}")
        return False

def get_all_guests():
    """Retrieve all guest data from database"""
    try:
        conn = get_db_connection()
        df = pd.read_sql_query("SELECT * FROM guests ORDER BY submission_date DESC", conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Error retrieving data: {str(e)}")
        return pd.DataFrame()

def validate_form(guest_data):
    """Validate the guest form data"""
    errors = []
    
    if not guest_data['first_name'].strip():
        errors.append("First name is required")
    
    if not guest_data['last_name'].strip():
        errors.append("Last name is required")
    
    if not guest_data['address_line1'].strip():
        errors.append("Address line 1 is required")
    
    if not guest_data['city'].strip():
        errors.append("City is required")
    
    if not guest_data['state']:
        errors.append("State is required")
    
    if not guest_data['zip_code'].strip():
        errors.append("ZIP code is required")
    
    # Email validation (if provided)
    if guest_data['email'].strip():
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, guest_data['email']):
            errors.append("Please enter a valid email address")
    
    return errors

def delete_guest_entry(guest_id):
    """Delete a guest entry from the database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM guests WHERE id = %s", (guest_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Error deleting entry: {str(e)}")
        return False

def show_success_screen():
    """Display success message after form submission"""
    st.markdown('<div class="success-container">', unsafe_allow_html=True)
    st.markdown("# 🎉 Thank You!")
    st.markdown(f"### Hi {st.session_state.get('submitted_guest_name', '')}!")
    st.markdown("Your address has been successfully submitted.")
    st.markdown("We'll be in touch soon with your wedding invitation! 💌")
    
    if st.button("✨ Submit Another Address", use_container_width=True):
        # Reset form state
        st.session_state['form_submitted'] = False
        st.session_state['submitted_guest_name'] = ""
        st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

# Main app
def main():
    # Initialize database
    if not init_database():
        st.error("Failed to initialize database. Please check your configuration.")
        st.stop()
    
    # Header
    st.markdown('<h1 class="main-header">💒 Wedding Guest Address Collection</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Please provide your address so we can send you your wedding invitation!</p>', unsafe_allow_html=True)
    
    # Initialize session state
    if 'admin_logged_in' not in st.session_state:
        st.session_state['admin_logged_in'] = False
    if 'form_submitted' not in st.session_state:
        st.session_state['form_submitted'] = False
    if 'submitted_guest_name' not in st.session_state:
        st.session_state['submitted_guest_name'] = ""
    
    # Sidebar for navigation
    st.sidebar.title("Navigation")
    
    # Show different options based on admin status
    if is_admin_logged_in():
        st.sidebar.success("👋 Welcome, Admin!")
        if st.sidebar.button("🚪 Logout"):
            admin_logout()
        
        page = st.sidebar.selectbox(
            "Choose a page:",
            ["📝 Guest Form", "📊 View Responses", "📥 Export Data"]
        )
    else:
        page = st.sidebar.selectbox(
            "Choose a page:",
            ["📝 Guest Form", "🔐 Admin Login"]
        )
    
    # Route to appropriate page
    if page == "📝 Guest Form":
        show_guest_form()
    elif page == "🔐 Admin Login":
        admin_login()
    elif page == "📊 View Responses":
        if is_admin_logged_in():
            show_responses()
        else:
            st.error("🔒 Access denied. Please login as admin to view responses.")
    elif page == "📥 Export Data":
        if is_admin_logged_in():
            show_export_options()
        else:
            st.error("🔒 Access denied. Please login as admin to export data.")

def show_guest_form():
    """Display the guest address collection form"""
    # Check if form was just submitted
    if st.session_state.get('form_submitted', False):
        show_success_screen()
        return
    
    st.markdown('<div class="form-container">', unsafe_allow_html=True)
    
    with st.form("guest_address_form"):
        st.subheader("📝 Guest Information")
        
        # Personal Information
        col1, col2 = st.columns(2)
        with col1:
            first_name = st.text_input("First Name *", placeholder="Enter first name")
            email = st.text_input("Email Address", placeholder="your.email@example.com")
        with col2:
            last_name = st.text_input("Last Name *", placeholder="Enter last name")
            phone = st.text_input("Phone Number", placeholder="(555) 123-4567")
        
        st.markdown("---")
        st.subheader("🏠 Address Information")
        
        # Address Information
        address_line1 = st.text_input("Address Line 1 *", placeholder="123 Main Street")
        address_line2 = st.text_input("Address Line 2", placeholder="Apt, Suite, etc. (optional)")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            city = st.text_input("City *", placeholder="City")
        with col2:
            state = st.selectbox("State *", [
                "", "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
                "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
                "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
                "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
                "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"
            ])
        with col3:
            zip_code = st.text_input("ZIP Code *", placeholder="12345")
        
        country = st.selectbox("Country", ["USA", "Canada", "Mexico", "Other"])
        
        # Submit button
        submitted = st.form_submit_button("💌 Submit Address", use_container_width=True)
        
        if submitted:
            # Collect form data
            guest_data = {
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
                'phone': phone,
                'address_line1': address_line1,
                'address_line2': address_line2,
                'city': city,
                'state': state,
                'zip_code': zip_code,
                'country': country
            }
            
            # Validate form
            errors = validate_form(guest_data)
            
            if errors:
                st.markdown('<div class="error-message">', unsafe_allow_html=True)
                st.error("Please fix the following errors:")
                for error in errors:
                    st.write(f"• {error}")
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                # Save data
                if save_guest_data(guest_data):
                    # Set session state for success screen
                    st.session_state['form_submitted'] = True
                    st.session_state['submitted_guest_name'] = first_name
                    st.rerun()
                else:
                    st.error("There was an error saving your information. Please try again.")
    
    st.markdown('</div>', unsafe_allow_html=True)

def show_responses():
    """Display all submitted responses (Admin only)"""
    st.subheader("📊 Guest Responses")
    
    df = get_all_guests()
    
    if df.empty:
        st.info("No responses yet.")
    else:
        st.write(f"Total responses: {len(df)}")
        
        # Display summary statistics
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Guests", len(df))
        with col2:
            states_count = df['state'].nunique()
            st.metric("States Represented", states_count)
        
        # Filter options
        st.subheader("Filter Responses")
        col1, col2 = st.columns(2)
        with col1:
            search_name = st.text_input("Search by name", placeholder="Enter first or last name")
        with col2:
            state_filter = st.selectbox("Filter by state", ["All"] + sorted(list(df['state'].unique())))
        
        # Apply filters
        filtered_df = df.copy()
        if search_name:
            filtered_df = filtered_df[
                filtered_df['first_name'].str.contains(search_name, case=False, na=False) |
                filtered_df['last_name'].str.contains(search_name, case=False, na=False)
            ]
        if state_filter != "All":
            filtered_df = filtered_df[filtered_df['state'] == state_filter]
        
        # Display filtered results
        if not filtered_df.empty:
            st.subheader("Guest Entries")
            
            # Display each entry with delete option
            for index, row in filtered_df.iterrows():
                with st.expander(f"👤 {row['first_name']} {row['last_name']} - {row['city']}, {row['state']}", expanded=False):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.write(f"**Name:** {row['first_name']} {row['last_name']}")
                        if row['email']:
                            st.write(f"**Email:** {row['email']}")
                        if row['phone']:
                            st.write(f"**Phone:** {row['phone']}")
                        st.write(f"**Address:** {row['address_line1']}")
                        if row['address_line2']:
                            st.write(f"**Address 2:** {row['address_line2']}")
                        st.write(f"**City:** {row['city']}")
                        st.write(f"**State:** {row['state']}")
                        st.write(f"**ZIP:** {row['zip_code']}")
                        st.write(f"**Country:** {row['country']}")
                        st.write(f"**Submitted:** {row['submission_date']}")
                    
                    with col2:
                        # Delete button with confirmation
                        if st.button(f"🗑️ Delete", key=f"delete_{row['id']}", help="Delete this entry"):
                            # Store the ID to delete in session state for confirmation
                            st.session_state[f'confirm_delete_{row["id"]}'] = True
                            st.rerun()
                        
                        # Show confirmation dialog if delete was clicked
                        if st.session_state.get(f'confirm_delete_{row["id"]}', False):
                            st.warning("⚠️ Are you sure?")
                            col_yes, col_no = st.columns(2)
                            with col_yes:
                                if st.button("✅ Yes", key=f"confirm_yes_{row['id']}"):
                                    if delete_guest_entry(row['id']):
                                        st.success("✅ Entry deleted successfully!")
                                        # Clear confirmation state
                                        if f'confirm_delete_{row["id"]}' in st.session_state:
                                            del st.session_state[f'confirm_delete_{row["id"]}']
                                        st.rerun()
                                    else:
                                        st.error("❌ Failed to delete entry.")
                            with col_no:
                                if st.button("❌ No", key=f"confirm_no_{row['id']}"):
                                    # Clear confirmation state
                                    if f'confirm_delete_{row["id"]}' in st.session_state:
                                        del st.session_state[f'confirm_delete_{row["id"]}']
                                    st.rerun()
            
            # Also show the data table for quick reference
            st.subheader("📋 Quick View Table")
            st.dataframe(
                filtered_df[['first_name', 'last_name', 'email', 'phone', 'city', 'state', 'submission_date']],
                use_container_width=True
            )
        else:
            st.info("No results match your filters.")

def show_export_options():
    """Show options for exporting guest data (Admin only)"""
    st.subheader("📥 Export Guest Data")
    
    df = get_all_guests()
    
    if df.empty:
        st.info("No data to export yet.")
        return
    
    # Export options
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📄 CSV Export")
        csv = df.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name=f"wedding_guests_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    
    with col2:
        st.subheader("📊 Excel Export")
        # Create Excel file in memory
        from io import BytesIO
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Guest List')
        
        excel_data = output.getvalue()
        
        st.download_button(
            label="Download Excel",
            data=excel_data,
            file_name=f"wedding_guests_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    
    # Data preview
    st.subheader("📋 Data Preview")
    st.dataframe(df.head(10), use_container_width=True)

if __name__ == "__main__":
    main() 