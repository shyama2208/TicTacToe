# Tic Tac Toe Django Channels Project

# Live URL : [URL](https://tictactoe-i2qb.onrender.com/)

## About the Author

This project was prepared and presented by Shyama, a skilled software developer specializing in Django and real-time web applications.

This project is a real-time Tic Tac Toe game application built using Django and Django Channels for WebSocket support. It implements asynchronous communication and game logic for multiplayer gameplay.

## Features
- Real-time gameplay using WebSockets.
- Django Channels integrated with Daphne ASGI server.
- Uses Django's ORM for database interactions.
- Separate ASGI and WSGI application configs.
- In-memory channel layers (can be updated to Redis for production).
- Frontend assets served with Django static files.

## Deployment

This project is ready for deployment on Render with the provided Procfile and configuration. See [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed deployment instructions.

## Environment Variables

Set the following environment variables for deployment:

- `DJANGO_SECRET_KEY` - Django secret key.
- `DJANGO_DEBUG` - Set to `False` for production.
- `DJANGO_ALLOWED_HOSTS` - Comma-separated list of hosts allowed.

## Author

This project was prepared and presented by Shyama.
