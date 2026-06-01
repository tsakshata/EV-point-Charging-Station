# EV Point

## Project Description
EV Point is a web application that helps users find nearby EV charging stations and book charging slots online.

## Features
- User Registration and Login
- Search EV Charging Stations
- Book Charging Slots
- User Profile Management
- Admin Dashboard
- Station Management
- Feedback System

## Technologies Used
- Python
- Flask
- MySQL
- HTML
- CSS
- JavaScript

## Database
Import the `EV_DB.sql` file into MySQL before running the application.

## Installation

1. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

2. Create the database using:
   ```sql
   EV_DB.sql
   ```

3. Update MySQL credentials in:
   ```python
   DBConnection.py
   ```

4. Run the application:
   ```bash
   python app.py
   ```

## Project Structure

- `app.py` - Main Flask application
- `DBConnection.py` - Database connection
- `templates/` - HTML templates
- `static/` - CSS, JavaScript, Images
- `EV_DB.sql` - Database schema

