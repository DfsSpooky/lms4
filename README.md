# Local Deployment Documentation

This guide describes how to deploy the LMS Academy project locally.

## Prerequisites

*   Python 3.12+
*   Git

## Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd <repository_name>
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    # Linux/Mac
    source venv/bin/activate
    # Windows
    venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    *(Note: If `requirements.txt` is missing, ensure you have Django, djangorestframework, django-cors-headers, and Pillow installed).*

4.  **Database Setup:**

    The project uses SQLite by default. Run the following commands to set up the database schema:

    ```bash
    python manage.py makemigrations academy
    python manage.py migrate
    ```

5.  **Populate Data:**

    To load initial data (categories, courses, sliders, certifications, and admin user), run:

    ```bash
    python populate_final.py
    ```

    *   **Admin User:** `admin` / `admin123`
    *   **Initial Data:** Includes "Hero Slides" and "Certification Cards" for the landing page.

## Running the Server

Start the Django development server:

```bash
python manage.py runserver
```

Access the application at: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

## Features

*   **Landing Page:** Includes dynamic Hero Slider and Certification Cards (populated via `populate_final.py`).
*   **Dashboards:**
    *   **Student:** View enrolled courses and progress.
    *   **Teacher:** Create and manage courses/modules/lessons (`/teacher/dashboard/`).
    *   **Admin:** Approve enrollments and manage user roles (`/admin-dashboard/`).
*   **Authentication:** Registration with extended profile fields (DNI, Address).
