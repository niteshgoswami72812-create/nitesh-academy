# Nitesh Academy - Fixed Django Project

## Correct folder structure

```text
NiteshAcademy_Fixed/
├── manage.py
├── requirements.txt
├── db.sqlite3
├── .env.example
├── .gitignore
├── project/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
└── myapp/
    ├── migrations/
    ├── static/
    ├── templates/
    ├── admin.py
    ├── apps.py
    ├── models.py
    ├── tests.py
    └── views.py
```

## Windows local setup

```bat
cd NiteshAcademy_Fixed
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Open: http://127.0.0.1:8000/

## Razorpay setup

Do not put secret keys directly in `settings.py` or GitHub.

In Command Prompt before `runserver`:

```bat
set RAZORPAY_KEY_ID=your_test_key_id
set RAZORPAY_KEY_SECRET=your_test_key_secret
```

PowerShell:

```powershell
$env:RAZORPAY_KEY_ID="your_test_key_id"
$env:RAZORPAY_KEY_SECRET="your_test_key_secret"
```

For Render, add the same variables in **Environment** along with:

- `DEBUG=False`
- `SECRET_KEY=<strong random secret>`
- `ALLOWED_HOSTS=<your-render-domain>.onrender.com`
- `CSRF_TRUSTED_ORIGINS=https://<your-render-domain>.onrender.com`

## Render commands

Build Command:

```bash
pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate
```

Start Command:

```bash
gunicorn project.wsgi:application
```

## Fixes included

- Removed duplicate/broken root Django files that conflicted with the real `project/` package.
- Cleaned WSGI/ASGI/settings files.
- Added WhiteNoise + `STATIC_ROOT` for deployment.
- Added Gunicorn dependency.
- Moved Razorpay credentials to environment variables.
- Recalculates payment amount on the Django server using database prices instead of trusting the browser-submitted total.
- Keeps Razorpay signature verification after payment.
- Removed `.git`, `__pycache__`, and `.pyc` junk from the deliverable.


## Razorpay local setup (important)

1. In Razorpay Dashboard, enable **Test Mode** and generate a NEW Test Key ID + Key Secret.
2. Open the `.env` file in this project.
3. Replace these two placeholder values only:

```env
RAZORPAY_KEY_ID=rzp_test_your_new_key_id
RAZORPAY_KEY_SECRET=your_new_key_secret
```

4. Install requirements and restart Django:

```powershell
python -m pip install -r requirements.txt
python manage.py runserver
```

The project now loads `.env` automatically using `python-dotenv`. Do not put the actual Razorpay key directly inside `settings.py`.

## Aurora Glass UI edition
This build includes `myapp/static/css/glassy.css`, a visual-only glassmorphism layer for the navbar, hero, cards, course catalog, forms, checkout and footer. Dark glass is the default theme; the existing theme toggle remains available. Razorpay/API secrets are intentionally not bundled in `.env`.
