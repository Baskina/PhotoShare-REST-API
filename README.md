# Contacts Management API - README

## Project Overview
This mini-project is a REST API built using FastAPI, designed for managing contacts and their information. The project uses SQLAlchemy as the ORM (Object Relational Mapper) to handle the database interactions, and PostgreSQL as the database. The API allows users to perform CRUD operations (Create, Read, Update, Delete) and includes additional features for searching and filtering contacts based on different attributes.

Additionally, the project now includes user authentication and authorization, ensuring that only registered users can perform operations on their own contacts using JWT tokens. Alembic is used for database migrations, and Docker Compose simplifies the setup of dependencies. Other enhancements include rate limiting, email verification, and avatar management.

## Key Features
- Store contacts with details such as:
  - First Name
  - Last Name
  - Email Address
  - Phone Number
  - Date of Birth
  - Additional Information (optional)
- Full CRUD operations for contacts.
- Search for contacts by:
  - First Name
  - Last Name
  - Email Address
- Retrieve contacts whose birthdays are in the upcoming 7 days.
- **Authentication and Authorization:**
  - User authentication is implemented using hashed passwords and JWT tokens (access and refresh tokens).
  - Users can only manage their own contacts.
  - Registration ensures no duplicate emails.
  - Secure password storage using hashing (passwords are never stored in plain text).
- **Email Verification**:
  - Newly registered users must verify their email address to activate their accounts.
- **Rate Limiting**:
  - Limits are enforced on the frequency of contact creation requests to prevent abuse.
- **User Avatar Upload**:
  - Users can upload and update their profile avatars via Cloudinary.
- **CORS (Cross-Origin Resource Sharing)**:
  - Enabled to allow secure API access from web-based clients.

## Technologies Used
- **FastAPI**: For building the REST API.
- **SQLAlchemy**: For database ORM.
- **PostgreSQL**: The database used for storing contact data.
- **Alembic**: For database migrations.
- **Pydantic**: For data validation and serialization.
- **JWT**: For implementing authentication and authorization.
- **Cloudinary**: For handling avatar image uploads.
- **Uvicorn**: ASGI server for serving FastAPI applications.
- **Docker Compose**: For containerizing the API and database services.

## Installation

### Clone the repository:
```bash
git clone <repository-url>
cd <project-directory>
```

### Set up a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Install the required dependencies:
```bash
pip install -r requirements.txt
```

### Configure environment variables:
1. All sensitive information should be stored in a `.env` file. To create file use .env.example as a example

### Run database migrations with Alembic:
run Postgres in docker
use db sql client (ex. DBeaver)
```bash
alembic init -t async migration

# change the file migration/env.py:
	from src.conf.config import config as app_config
	from src.entity.models import Base
...
    target_metadata = Base.metadata
    config.set_main_option("sqlalchemy.url", app_config.DB_URL)
    
```bash
alembic revision --autogenerate -m 'Init'
alembic upgrade head
```

### Start the FastAPI server:

run Redis in docker
```bash
uvicorn main:app --reload
```

### Docker Compose Setup
To use Docker Compose to set up the application and database:
1. Make sure you have Docker and Docker Compose installed.
2. In the project root directory, use the following command to start all services:
   ```bash
   docker-compose up -d
   ```
3. This will automatically build and start the API and database services.

### API Documentation
After starting the server, navigate to `http://127.0.0.1:8000/docs` to explore the API documentation via the FastAPI Swagger UI.

## API Endpoints

### Photo management

- **Create a new photo**
- `POST /api/photos/`
- Create a new photo with a description
- available to all users

- **Delete photo by ID**
- `DELETE /api/photos/{photo_id}`
- Delete photo from the database and from Cloud
- Available only to photo owners and administrators

- **Update photo description by ID**
- `PUT /api/photos/{photo_id}`
- Update description of an existing photo
- Available only to photo owners and administrators

- **Get a photo by ID**
- `GET /api/photos/{photo_id}`
- Get a specific photo by its ID
- Available to all users

- **Get a list of photos for the current user**
- `GET /api/photos/`
- Get a list of all your photos
- available to all users

### Authentication Endpoints

- **Sign up (user registration)**
  - `POST /api/auth/signup`
  - Create a new user account with email and password.

- **Login**
  - `POST /api/auth/login`
  - Authenticate a user with email and password. Returns JWT access and refresh tokens.

- **Refresh Token**
  - `GET /api/auth/refresh_token`
  - Refresh the JWT access token using a valid refresh token.

- **Verify Email**
  - `GET /api/auth/verify-email?token=<verification_token>`
  - Activate a user account by verifying their email.

### Avatar Management

- **Update Avatar**
  - `POST /api/users/avatar`
  - Upload or update the user’s profile avatar. The image is stored on Cloudinary.

### Additional functions
- **Photo search**
- `GET /api/photos/search`
- Search for photos by keyword in description and by tag, as well as filter by rating and by photo creation date.

- **Photo search by author**
- `GET /api/photos/search/{user_id}`
- Search for photos by photo author: by user ID and by username.

- **Transforms a photo**
- `GET /api/photos/{photo_id}/transform`
- Transforms a photo by applying various modifications such as resizing, cropping, rotating, and adding effects..

- **Photo rating**
- `PUT /api/photos/{photo_id}/rating`
- Rate a photo from 0 to 5. Calculates the photo rating - the average value of all likes. The rating value for unrated photos is Null.
- You can rate a photo only once. You cannot rate your own photo.

- **View all likes for a photo**
- `GET /api/photos/{photo_id}/rating`
- View all likes for a photo by photo ID.
- Only available to moderators and administrators.

- **Delete likes for a photo**
- `GET /api/photos/rating/{like_id}`
- Delete likes for a photo by like ID.
- Only available to moderators and administrators.

## Authentication & Authorization
The project includes authentication and authorization mechanisms to restrict access to registered users only.

- **User registration**
  - If a user with the provided email already exists, the server returns `HTTP 409 Conflict`.
  - The password is hashed before storage to ensure security.
  - On successful registration, the server responds with `HTTP 201 Created` and returns the new user’s details.

- **Email Verification**
  - On registration, users receive a verification link via email. They must verify their email before accessing the API.

- **Login and JWT Tokens**
  - On login, users provide their email and password. If the credentials are incorrect, the server returns `HTTP 401 Unauthorized`.
  - The authentication mechanism uses a pair of tokens: an `access_token` and a `refresh_token` for authorization.

- **Access Restrictions**
  - Users can only access and modify their own contacts.
  - All POST operations return a `201 Created` status on success.

## General Requirements
- The project is built with FastAPI.
- Uses SQLAlchemy ORM to interact with the PostgreSQL database.
- Includes full CRUD functionality for managing contacts.
- Authentication and authorization using JWT tokens.
- Supports data validation through Pydantic.
- Exposes API documentation through FastAPI’s built-in Swagger interface.
- Rate limiting is applied to restrict request frequency.
- CORS is enabled to control cross-origin requests.
- Docker Compose is used for managing services, including the database and API.

## License
This project is licensed under the MIT License - see the LICENSE file for details.

---