# Mind Check 

## Installation Steps:

1. Create a virtual environment:
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

2. Install dependencies:
   pip install -r requirements.txt

3. Create the Django app structure:
   python manage.py startapp app

4. Run migrations:
   python manage.py makemigrations
   python manage.py migrate


5. Run the development server:
   python manage.py runserver

6. Visit the application:
   http://localhost:8000



## Features Implemented:

✓ Home, About, Pricing, Contacts pages
✓ User Authentication (Register/Login/Logout)
✓ Insights System (Create, Read, Update, Delete articles)
✓ Consultation Booking (List psychologists, book consultations)
✓ M-Pesa Payment Integration
✓ Responsive Bootstrap UI
✓ Admin Dashboard (Manage users, articles, bookings)
× Chat System (Real-time messaging between users)




