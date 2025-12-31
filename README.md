# FastAPI Backend Template

🚀 Based on the [Full Stack FastAPI Template](https://github.com/fastapi/full-stack-fastapi-template) by [Sebastián Ramírez](https://github.com/tiangolo)

A modern, production-ready FastAPI backend template with authentication, email support, and PostgreSQL database.

## Technology Stack and Features

- ⚡ [**FastAPI**](https://fastapi.tiangolo.com) for the Python backend API.
  - 🧰 [SQLModel](https://sqlmodel.tiangolo.com) for the Python SQL database interactions (ORM).
  - 🔍 [Pydantic](https://docs.pydantic.dev), used by FastAPI, for the data validation and settings management.
  - 💾 [PostgreSQL](https://www.postgresql.org) as the SQL database.
- 🐋 [Docker Compose](https://www.docker.com) for development and production.
- 🔒 Secure password hashing by default.
- 🔑 JWT (JSON Web Token) authentication.
- 📫 Email based password recovery and account activation.
- ✅ Tests with [Pytest](https://pytest.org).
- 📞 [Nginx](https://nginx.org) as a reverse proxy.
- 🚢 Deployment instructions using Docker Compose.
- 🏭 CI (continuous integration) and CD (continuous deployment) based on GitHub Actions.

## How To Use It

You can **fork or clone** this repository and use it as is.

### Configure

Update configs in the `.env` file to customize your configurations.

Before deploying, make sure you change at least the values for:

- `SECRET_KEY`
- `FIRST_SUPERUSER_PASSWORD`
- `POSTGRES_PASSWORD`

You can (and should) pass these as environment variables from secrets.

Read the [deployment.md](./deployment.md) docs for more details.

### Generate Secret Keys

Some environment variables in the `.env` file have a default value of `changethis`.

You have to change them with a secret key. To generate secret keys, run the following command:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Copy the content and use that as password / secret key. Run that again to generate another secure key.


## Build Email Templates

```bash
npm install mjml
cd ./backend/app/email-templates/src/

npx mjml ./new_account.mjml -o ../build/new_account.html
npx mjml ./confirm_signup.mjml -o ../build/confirm_signup.html
npx mjml ./reset_password.mjml -o ../build/reset_password.html
npx mjml ./activate_account.mjml -o ../build/activate_account.html
```

## Backend Development

Backend docs: [backend/README.md](./backend/README.md).

## Deployment

Deployment docs: [deployment.md](./deployment.md).

## Development

General development docs: [development.md](./development.md).

This includes using Docker Compose, custom local domains, `.env` configurations, etc.


## Credits

This project is based on the [Full Stack FastAPI Template](https://github.com/fastapi/full-stack-fastapi-template).

**Original Author:** Sebastián Ramírez ([@tiangolo](https://github.com/tiangolo))
**Original License:** MIT License
**Modified by:** Abdoulaye Dabo

Thanks to Sebastián Ramírez for his excellent work on FastAPI and its templates.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
