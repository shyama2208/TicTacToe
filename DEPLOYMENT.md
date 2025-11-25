# Deployment Instructions for Render

This document outlines steps to deploy the Tic Tac Toe Django Channels application on [Render](https://render.com/).

---

## Prerequisites
- You have a Render account.
- You have connected the Git repository containing this project to Render.

---

## Environment Variables

Set the following environment variables in the Render dashboard for your service:

- `DJANGO_SECRET_KEY`: Your Django secret key. **Do NOT use the default insecure key in production.**
- `DJANGO_DEBUG`: Set to `False` for production environment.
- `DJANGO_ALLOWED_HOSTS`: Comma-separated list of hostnames allowed, e.g. `yourapp.onrender.com`
- Any other environment variables your project requires.

---

## Procfile

The included `Procfile` defines the web process:

```
web: daphne -b 0.0.0.0 -p 8000 tic_tac_toe.asgi:application
```

Render will use this command to start the ASGI server with Daphne.

---

## Static Files

The project uses Django's `collectstatic` management command to collect static files into a single directory for serving.

Before deployment or as part of Render's build commands, run:

```
python manage.py collectstatic --noinput
```

Ensure the `STATIC_ROOT` is set in `settings.py` (currently set to `<BASE_DIR>/staticfiles`).

---

## Database

By default, this project uses SQLite database. For production deployments, it is recommended to use a production-ready database like PostgreSQL.

Render provides managed PostgreSQL databases which you can configure. Update your `DATABASES` settings accordingly if you switch to another database.

---

## Channel Layers

Currently, the project uses the in-memory channel layer backend, which is suitable for development or single-instance deployments.

For multi-instance deployments or production, it is recommended to switch to Redis channel layer.

---

## Deployment Steps on Render

1. Connect your Git repository on Render.
2. Create a new Web Service using Docker or Python environment.
3. Set environment variables mentioned above.
4. Set the Build Command to:

```
pip install -r requirements.txt
python manage.py collectstatic --noinput
```

5. Set the Start Command (or leave as default) to:

```
daphne -b 0.0.0.0 -p 8000 tic_tac_toe.asgi:application
```

6. Deploy and monitor logs for errors.

---

## Additional Notes

- Ensure you do **not** commit sensitive information like secret keys or environment files to the repository.
- For better security, do not use Django Debug mode (`DEBUG=True`) in production.
- Consider configuring HTTPS and other security best practices on Render.

---

By following these instructions, you should be able to deploy and run the Tic Tac Toe Django Channels application on Render smoothly.
