import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
import sqlite3
from pathlib import Path
import hashlib

from supabase import create_client, Client
import re


# Page configuration
st.set_page_config(
    page_title="Wedding Guest Addresses",
    page_icon="💒",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Get admin credentials from Streamlit secrets
def get_admin_credentials():
    """Get admin credentials from Streamlit secrets"""
    try:
        username = st.secrets["ADMIN_USERNAME"]
        password = st.secrets["ADMIN_PASSWORD"]
        return username, password
    except KeyError as e:
        st.error(f"Missing secret: {e}. Please configure ADMIN_USERNAME and ADMIN_PASSWORD in .streamlit/secrets.toml")
        st.stop()
    except Exception as e:
        st.error(f"Error reading secrets: {e}")
        st.stop()

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #FF6B9D;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .sub-header {
        font-size: 1.5rem;
        color: #4A4A4A;
        text-align: center;
        margin-bottom: 2rem;
    }
    .form-container {
        background-color: #f8f9fa;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
    .success-message {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #c3e6cb;
        margin: 1rem 0;
    }
    .error-message {
        background-color: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #f5c6cb;
        margin: 1rem 0;
    }
    .success-screen {
        background-color: #d4edda;
        padding: 3rem;
        border-radius: 20px;
        border: 2px solid #c3e6cb;
        margin: 2rem 0;
        text-align: center;
    }
    .success-icon {
        font-size: 4rem;
        color: #28a745;
        margin-bottom: 1rem;
    }
    .success-title {
        font-size: 2.5rem;
        font-weight: bold;
        color: #155724;
        margin-bottom: 1rem;
    }
    .success-text {
        font-size: 1.2rem;
        color: #155724;
        margin-bottom: 2rem;
    }
    .stButton > button {
        background-color: #FF6B9D;
        color: white;
        border-radius: 25px;
        padding: 0.5rem 2rem;
        font-weight: bold;
        border: none;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    .stButton > button:hover {
        background-color: #E55A8A;
        box-shadow: 0 4px 8px rgba(0,0,0,0.3);
    }
    .admin-login {
        background-color: #fff3cd;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #ffeaa7;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


# Initialize Supabase connection
@st.cache_resource
def init_supabase():
    """Initialize connection to Supabase"""
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        return create_client(url, key)
    except KeyError as e:
        st.error(f"Missing secret: {e}. Please configure SUPABASE_URL and SUPABASE_KEY in secrets.")
        st.stop()
    except Exception as e:
        st.error(f"Failed to connect to Supabase: {e}")
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

# Initialize database
def init_database():
    """Initialize Supabase database for storing guest addresses"""
    try:
        supabase = init_supabase()
        
        # Create table using Supabase RPC (SQL function)
        # Note: In Supabase, you typically create tables through the dashboard or SQL editor
        # This is just to ensure the table structure is as expected
        
        # Check if the table exists by trying to query it
        result = supabase.table("guests").select("id").limit(1).execute()
        return True
    except Exception as e:
        # If table doesn't exist, provide instructions
        st.error(f"Please ensure the 'guests' table exists in your Supabase database. You can create it using the SQL editor in Supabase dashboard with this SQL:")
        st.code('''
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
);
        ''')
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
    """Save guest data to Supabase database"""
    try:
        supabase = init_supabase()
        
        # Prepare data for insertion
        data = {
            "first_name": guest_data['first_name'],
            "last_name": guest_data['last_name'],
            "email": guest_data['email'] if guest_data['email'] else None,
            "phone": guest_data['phone'] if guest_data['phone'] else None,
            "address_line1": guest_data['address_line1'],
            "address_line2": guest_data['address_line2'] if guest_data['address_line2'] else None,
            "city": guest_data['city'],
            "state": guest_data['state'],
            "zip_code": guest_data['zip_code'],
            "country": guest_data['country']
        }
        
        # Insert data using Supabase
        result = supabase.table("guests").insert(data).execute()

        
        return True
    except Exception as e:
        st.error(f"Error saving data: {str(e)}")
        return False

@st.cache_data(ttl=60)  # Cache for 1 minute
def get_all_guests():
    """Retrieve all guest data from Supabase database"""
    try:

        supabase = init_supabase()
        
        # Get all guests ordered by submission_date descending
        result = supabase.table("guests").select("*").order("submission_date", desc=True).execute()
        
        # Convert to DataFrame
        if result.data:
            df = pd.DataFrame(result.data)
            # Convert submission_date to datetime if it exists
            if 'submission_date' in df.columns:
                df['submission_date'] = pd.to_datetime(df['submission_date'])
            return df
        else:
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Error retrieving data: {str(e)}")
        return pd.DataFrame()

def validate_form(guest_data):
    """Validate form data"""
    errors = []
    
    if not guest_data['first_name'].strip():
        errors.append("First name is required")
    if not guest_data['last_name'].strip():
        errors.append("Last name is required")
    if not guest_data['address_line1'].strip():
        errors.append("Address is required")
    if not guest_data['city'].strip():
        errors.append("City is required")
    if not guest_data['state'].strip():
        errors.append("State is required")
    if not guest_data['zip_code'].strip():
        errors.append("ZIP code is required")
    
    # Email validation
    if guest_data['email'] and '@' not in guest_data['email']:
        errors.append("Please enter a valid email address")
    
    return errors

def delete_guest_entry(guest_id):
    """Delete a guest entry from the Supabase database"""
    try:

        supabase = init_supabase()
        
        # Delete the guest entry by ID
        result = supabase.table("guests").delete().eq("id", guest_id).execute()
        
        return True
    except Exception as e:
        st.error(f"Error deleting entry: {str(e)}")
        return False

# Main app
def main():
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

def show_success_screen():
    """Display success screen after form submission"""
    st.markdown('<div class="success-screen">', unsafe_allow_html=True)
    st.markdown('<div class="success-icon">🎉</div>', unsafe_allow_html=True)
    st.markdown('<div class="success-title">Thank You!</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="success-text">Hi {st.session_state.submitted_guest_name}!<br><br>Your address has been successfully submitted.<br>We\'ll be in touch soon with your wedding invitation!</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Add some spacing
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Button to submit another address
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("📝 Submit Another Address", use_container_width=True):
            st.session_state['form_submitted'] = False
            st.session_state['submitted_guest_name'] = ""
            st.rerun()

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
            states_count = int(df['state'].nunique())
            st.metric("States Represented", states_count)
        
        # Filter options
        st.subheader("Filter Responses")
        col1, col2 = st.columns(2)
        with col1:
            search_name = st.text_input("Search by name", placeholder="Enter first or last name")
        with col2:
            state_filter = st.selectbox("Filter by state", ["All"] + list(df['state'].unique()))
        
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
        
        # Write Excel data
        df.to_excel(output, index=False, sheet_name='Guest List', engine='openpyxl')
        excel_data = output.getvalue()
        
        st.download_button(
            label="Download Excel",
            data=excel_data,
            file_name=f"wedding_guests_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    
    # Clean up temporary file
    if os.path.exists('temp_wedding_guests.xlsx'):
        os.remove('temp_wedding_guests.xlsx')
    
    # Data preview
    st.subheader("📋 Data Preview")
    st.dataframe(df.head(10), use_container_width=True)

if __name__ == "__main__":
    main() 