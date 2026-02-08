# Campus Event Scheduling and Space Management System

## Prerequisites

Before running this project, ensure you have the following installed:

- **Python 3.7 or higher**
- **MySQL Server 8.0 or higher**
- **MySQL Workbench** (for database management)
- **pip** (Python package manager)

## Installation

### 1. Install Required Dependencies

```bash
pip install Flask
pip install Flask-SQLAlchemy
pip install Flask-Login
pip install Flask-WTF
pip install MySQLdb
pip install mysql-connector-python
```

### 2. Set Up the Database Using MySQL Workbench

#### Step 1: Open MySQL Workbench and Connect

1. Open **MySQL Workbench**
2. Connect to your MySQL Server using your credentials

#### Step 2: Create the Database

1. In MySQL Workbench, open a new SQL query tab
2. Run the following command:
   ```sql
   CREATE DATABASE event_space_management;
   ```
3. Click the **Execute** button (lightning icon) or press `Ctrl+Enter`

#### Step 3: Import the Database Schema

1. Go to **Server** → **Data Import**
2. Select **Import from Self-Contained File**
3. Browse and select the `Dump.sql` file from your project folder
4. Select **event_space_management** as the target schema
5. Click **Start Import**

Alternatively, you can copy the contents of `Dump.sql` into a new query tab and execute it:
```sql
USE event_space_management;
-- Then paste the contents of Dump.sql here
```

### 3. Configure the Application

Open `app.py` and verify/update the database configuration:

```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqldb://root:yourpassword@localhost/event_space_management'
```

**Note**: Update the credentials (`root` and password) if your MySQL credentials are different.

### 4. Create Required Folders (if not exists)

```bash
# Create static images folder if needed
mkdir -p static/images
```

## Running the Application

```bash
python3 app.py
```

Or alternatively:
```bash
flask run
```

Then open your web browser and navigate to:
```
http://localhost:5000
```

## Default Login Credentials

After importing the database dump, you can use the following test credentials:

- **Admin**: Check the database for admin accounts
- **Lecturer**: Check the database for lecturer accounts  
- **Organizer**: Check the database for organizer accounts
- **Student**: You can create a new student account through the signup page

## Project Structure

```
├── app.py                      # Main Flask application
├── auth.py                     # Authentication blueprint
├── models.py                   # Database models
├── forms.py                    # WTForms for form handling
├── admin_view.py              # Admin dashboard routes
├── lecturer_view.py           # Lecturer dashboard routes
├── organizer_view.py          # Organizer dashboard routes
├── student_view.py            # Student dashboard routes
├── flask_app.py               # Additional Flask configuration
├── Dump.sql                   # Database schema and sample data
├── static/                    # Static files (CSS, images, JavaScript)
│   ├── css/                   # Stylesheets
│   ├── images/                # Image assets
│   └── temp/                  # Temporary files
├── templates/                 # HTML templates
│   ├── admin/                 # Admin templates
│   ├── lecturer/              # Lecturer templates
│   ├── organizer/             # Organizer templates
│   ├── student/               # Student templates
│   ├── login.html             # Login page
│   ├── index.html             # Home page
│   └── ...
└── README.md                  # This file
```

## Troubleshooting

### Database Connection Error
- Ensure MySQL is running
- Check database credentials in `app.py`
- Verify the database `event_space_management` exists
- Confirm MySQL user has proper permissions

### Module Not Found Errors
- Ensure all packages are installed: `pip install -r requirements.txt`
- Check that virtual environment is activated
- Verify Python version is 3.7 or higher

### Port Already in Use
- Change the port in `app.py`:
  ```python
  app.run(debug=True, port=5001)
  ```

### Static Files Not Loading
- Ensure `static/` folder exists
- Check CSS and image file paths in templates
- Clear browser cache (Ctrl+Shift+Delete or Cmd+Shift+Delete)

## Features in Development

- Email notifications for event updates
- Advanced analytics and reporting
- Mobile application
- Calendar integration

## Support and Contribution

For issues, questions, or contributions, please contact the development team or create an issue in the project repository.

## License

This project is provided as-is for educational and institutional use.

## Version

**Version**: 1.0.0  
**Last Updated**: February 2026
