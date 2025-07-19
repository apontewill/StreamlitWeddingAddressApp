# Wedding Address Collection App Configuration

# App Settings
APP_TITLE = "Wedding Guest Address Collection"
APP_ICON = "💒"
PAGE_TITLE = "Wedding Guest Addresses"

# Wedding Details (customize these for your wedding)
WEDDING_COUPLE = "John & Jane"
WEDDING_DATE = "June 15, 2024"
WEDDING_LOCATION = "Beautiful Venue, City, State"

# Form Settings
REQUIRED_FIELDS = [
    "first_name",
    "last_name", 
    "address_line1",
    "city",
    "state",
    "zip_code"
]

# Available countries
COUNTRIES = ["USA", "Canada", "Mexico", "Other"]

# US States
US_STATES = [
    "", "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
    "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
    "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
    "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
    "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"
]

# Custom CSS Colors (you can change these to match your wedding theme)
PRIMARY_COLOR = "#FF6B9D"  # Pink
SECONDARY_COLOR = "#E55A8A"  # Darker pink
SUCCESS_COLOR = "#d4edda"  # Light green
ERROR_COLOR = "#f8d7da"  # Light red

# Success message
SUCCESS_MESSAGE = "🎉 Thank you! Your address has been successfully submitted."
SUCCESS_SUBTEXT = "We'll be in touch soon with your wedding invitation!"

# Form placeholders
PLACEHOLDERS = {
    "first_name": "Enter first name",
    "last_name": "Enter last name", 
    "email": "your.email@example.com",
    "phone": "(555) 123-4567",
    "address_line1": "123 Main Street",
    "address_line2": "Apt, Suite, etc. (optional)",
    "city": "City",
    "zip_code": "12345"
} 