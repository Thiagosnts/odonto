# Dental Admin v3


Dental clinic administration system.

# Technical details



# Modules:

- Dashboard
- Users
- Patients
- Treatments
- Treatments sequences
- Reports

# Features:

- Users register and login.
- User roles (admin, office, doctor) with diferent views.
- User profile image upload.
- Data search filter and pagination.
- Entry data validation.
- Create patients diagnostics.
- Create treatment sequence directly from patient diagnostic.
- Open, proccess, cancel and close treatment sequence.
- Email invoice directly to patient.
- Report of total income from all treatments.
- Report of total earned from each doctor (40% of total income from their treatments).


# instrucoes:

- virtualenv .venv
- source .venv/bin/activate
- pip install -r requirements.txt
- docker-compose up -d
- python manage.py runserver
