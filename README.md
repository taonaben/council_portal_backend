
# Council Portal Backend ![Python](https://img.shields.io/badge/Python-3.8%2B-blue) ![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

## Description

Council Portal Backend is a robust backend service designed to power council or committee management systems. It provides secure APIs, user authentication, meeting management, and document handling to streamline council operations and collaboration.

## Features

- User authentication and authorization (JWT-based)
- Council member and committee management
- Meeting scheduling and minutes recording
- Document upload and sharing
- Role-based access control
- RESTful API endpoints
- Admin dashboard support
- Audit logs and activity tracking

## Demo

[API Documentation](https://council-portal.onrender.com/api/schema/swagger-ui/)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/taonaben/council_portal_backend.git
   cd council_portal_backend
   ```
2. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up environment variables (see [Configuration](#configuration) below).

5. Initialize the database:
   ```bash
   python manage.py migrate
   ```

6. Run the development server:
   ```bash
   python manage.py runserver
   ```

## Usage

- Access the API at `https://council-portal.onrender.com/api/schema/swagger-ui/`
- Use API documentation (e.g., Swagger/OpenAPI if available) for endpoint details
- Example request (login):
   ```bash
   curl -X POST https://council-portal.onrender.com/api/auth/login/ \
     -H 'Content-Type: application/json' \
     -d '{"username": "admin", "password": "yourpassword"}'
   ```

## Configuration

Create a `.env` file in the project root with the following variables:

```env
SECRET_KEY=your-secret-key
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3
ALLOWED_HOSTS=localhost,127.0.0.1
EMAIL_HOST=your-email-host
EMAIL_HOST_USER=your-email-user
EMAIL_HOST_PASSWORD=your-email-password
```
Adjust as needed for your environment and deployment.

## Tech Stack

- Python 3.8+
- Django / Django REST Framework
- PostgreSQL or SQLite (configurable)
- JWT Authentication
- Celery (for background tasks, if used)
- Docker (optional, for containerization)
- HTML, CSS, JavaScript (for admin or dashboard if applicable)

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a new branch: `git checkout -b feature/your-feature`
3. Make your changes and commit: `git commit -m 'Add your feature'`
4. Push to your fork: `git push origin feature/your-feature`
5. Submit a Pull Request

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for more details.

## License

This project is licensed under the [MIT License](LICENSE).

## Contact / Acknowledgments

- Author: [taonaben](https://github.com/taonaben)
- For questions or support, open an issue or contact via email: munikwataona09@gmail.com

Special thanks to all contributors and the open-source community for their support and tools.
