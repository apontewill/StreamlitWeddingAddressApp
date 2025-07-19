# 💒 Wedding Guest Address Collection App

A beautiful and user-friendly Streamlit application for collecting wedding guest addresses with secure admin access.

## Features

- **📝 Guest Form**: Collect guest information including:
  - Personal details (name, email, phone)
  - Complete address information

- **🔐 Admin Authentication**: Secure access to admin features
  - Password-protected admin login
  - Session management
  - Configurable credentials

- **📊 View Responses** (Admin Only): 
  - See all submitted responses
  - Filter by name or state
  - View summary statistics
  - Real-time data updates

- **📥 Export Data** (Admin Only): 
  - Export to CSV format
  - Export to Excel format
  - Data preview functionality

- **🎨 Modern UI**: 
  - Beautiful, responsive design
  - Wedding-themed styling
  - Form validation
  - Success/error messages

## Security Features

- **Admin-only access** to view responses and export data
- **Configurable credentials** via `.streamlit/secrets.toml`
- **Streamlit Cloud secrets** support for production
- **Session management** with logout functionality
- **Access control** with clear error messages

## Local Development

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. Clone or download this repository
2. Navigate to the project directory:
   ```bash
   cd streamlit_apps/wedding_addresses
   ```

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. **IMPORTANT**: Change admin credentials in `.streamlit/secrets.toml`:
   ```python
   ADMIN_USERNAME = "your_username"
   ADMIN_PASSWORD = "your_secure_password"
   ```

5. Run the Streamlit app:
   ```bash
   streamlit run app.py
   ```

6. Open your browser and go to `http://localhost:8501`

### Default Admin Credentials

**⚠️ SECURITY WARNING**: The default credentials are:
- Username: `admin`
- Password: `wedding2024`

**You MUST change these before deploying!**

## Deployment to Streamlit Cloud

### Step 1: Prepare Your Repository

1. Make sure your code is in a GitHub repository
2. **Change admin credentials** in `.streamlit/secrets.toml`
3. Ensure you have the following files in your repository:
   - `app.py` (main application file)
   - `requirements.txt` (dependencies)
   - `.streamlit/secrets.toml` (admin credentials)
   - `README.md` (optional but recommended)

### Step 2: Deploy to Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with your GitHub account
3. Click "New app"
4. Fill in the deployment form:
   - **Repository**: Select your GitHub repository
   - **Branch**: Choose the branch (usually `main` or `master`)
   - **Main file path**: Enter `streamlit_apps/wedding_addresses/app.py`
   - **App URL**: Choose a unique URL for your app
5. Click "Deploy!"

### Step 3: Configure Secure Admin Credentials (Recommended)

For production deployment, use Streamlit Cloud secrets instead of the config file:

1. Go to your app's settings in Streamlit Cloud
2. Navigate to the "Secrets" section
3. Add the following secrets:
   ```toml
   [secrets]
   ADMIN_USERNAME = "your_secure_username"
   ADMIN_PASSWORD = "your_very_secure_password"
   ```
4. Save the secrets

The app will automatically use these secure credentials instead of the config file.

### Step 4: Configure App Settings (Optional)

After deployment, you can configure additional settings:

1. Configure environment variables if needed
2. Set up custom domains (if you have one)
3. Configure email notifications

## Admin Access

### Logging In as Admin

1. Navigate to the app
2. Select "🔐 Admin Login" from the sidebar
3. Enter your admin credentials
4. Access "📊 View Responses" and "📥 Export Data" pages

### Admin Features

- **View all guest responses** with filtering options
- **Export data** in CSV or Excel format
- **Search and filter** guest information
- **Session management** with logout functionality

## Data Storage

The app uses SQLite database (`wedding_guests.db`) to store guest information. The database is automatically created when the app runs for the first time.

### Database Schema

The `guests` table includes the following fields:
- `id`: Unique identifier
- `first_name`: Guest's first name
- `last_name`: Guest's last name
- `email`: Email address
- `phone`: Phone number
- `address_line1`: Primary address
- `address_line2`: Secondary address (optional)
- `city`: City
- `state`: State
- `zip_code`: ZIP code
- `country`: Country
- `rsvp_status`: RSVP status (default: Pending)
- `submission_date`: When the form was submitted

## Customization

### Changing Admin Credentials

1. **For local development**: Edit `.streamlit/secrets.toml`
2. **For production**: Use Streamlit Cloud secrets (recommended)

### Changing the Theme

You can customize the app's appearance by modifying the CSS in the `app.py` file. Look for the `st.markdown` section with custom CSS styles.

### Adding New Fields

To add new fields to the form:

1. Add the field to the form in the `show_guest_form()` function
2. Update the database schema in the `init_database()` function
3. Add the field to the `save_guest_data()` function
4. Update the validation in `validate_form()` if needed

### Modifying Validation Rules

Edit the `validate_form()` function to add or modify validation rules for the form fields.

## Security Considerations

- **Change default admin credentials** before deploying
- **Use Streamlit Cloud secrets** for production credentials
- **Consider implementing session timeout** for added security
- **Monitor admin access** and consider logging admin actions
- **Use HTTPS** for production deployment (automatic with Streamlit Cloud)
- **Consider rate limiting** to prevent spam submissions

## Troubleshooting

### Common Issues

1. **Import errors**: Make sure all dependencies are installed
2. **Database errors**: Check file permissions for the database file
3. **Deployment issues**: Verify the file path in Streamlit Cloud settings
4. **Admin login issues**: Verify credentials in `.streamlit/secrets.toml` or Streamlit secrets
5. **Access denied**: Make sure you're logged in as admin to access protected pages

### Getting Help

If you encounter issues:
1. Check the Streamlit documentation
2. Review the error messages in the Streamlit Cloud logs
3. Test the app locally first
4. Verify admin credentials are correctly configured

## License

This project is open source and available under the MIT License.

## Contributing

Feel free to submit issues and enhancement requests!

---

**Happy Wedding Planning! 💕** 