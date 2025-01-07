# PhotoShare API - README

## Project Overview
This mini-project is a REST API built using FastAPI, designed for managing photos, comments, and ratings. The project uses SQLAlchemy as the ORM (Object Relational Mapper) to handle database interactions, and PostgreSQL as the database. The API allows users to upload photos, add comments, and rate photos. Additional features include advanced image transformations, searching for photos by tags and descriptions, and user avatar management.

Additionally, the project includes user authentication and authorization, ensuring that only registered users can upload and manage their own photos and comments using JWT tokens. Alembic is used for database migrations, and Docker Compose simplifies the setup of dependencies. Other enhancements include rate limiting, email verification, avatar management through Cloudinary, and photo transformation features such as resizing, cropping, and rotating.

Explore the deployed application here: https://photoshare-rest-api.koyeb.app/


## Key Features
### Photo Management
- Upload photos with descriptions and tags.
- Advanced photo transformations (resizing, cropping, rotating, and applying effects).
- Search photos by:
  - Keywords in descriptions.
  - Tags.
  - Ratings.
  - Creation date range.
- Manage photo metadata (update descriptions, delete photos).

### Comment Management
- Add comments under photos.
- Edit or update comments by their authors.
- Moderators and administrators can delete inappropriate comments.

### Photo Rating
- Users can rate photos on a scale of 0–5.
- Ratings are averaged to calculate the overall photo score.
- Only authenticated users can rate photos, and self-rating is restricted.

- **Authentication and Authorization:**
  - User authentication is implemented using hashed passwords and JWT tokens (access and refresh tokens).
  - Users are assigned one of the following roles:
  - **Regular User**: Can manage their own photos and comments.
  - **Moderator**: Can delete comments from any user.
  - **Administrator**: Full access to manage all photos, comments, and user roles.
  - Users can only manage their own content (photos and comments) unless they are moderators or administrators.
  - Registration ensures no duplicate emails.
  - Secure password storage using hashing (passwords are never stored in plain text).
- **Email Verification**:
  - Newly registered users must verify their email address to activate their accounts.
   - Verification emails are sent using FastAPI-Mail, which includes:
    - A personalized greeting with the user's name.
    - A secure verification link containing a JWT token.
  - The verification link is generated dynamically and directs the user to an endpoint where their email is confirmed.
  - Email templates are stored in the `templates` folder (e.g., `verify_email.html`) and can be customized to fit the application's needs.
  - If an error occurs during email sending, it is logged for debugging and troubleshooting.
  - The verification link and token have a limited validity period for security purposes (if implemented).
- **Rate Limiting**:
- Rate limiting is implemented to ensure fair usage and prevent abuse of the API.
  - Limits the number of requests a user can make within a specified time window.
  - Prevents overloading the server with excessive requests.
  - Returns an `HTTP 429 Too Many Requests` status code when the limit is exceeded.
  - Customizable rate limits can be applied to specific API endpoints (e.g., limiting photo creation requests to 10 per minute).
  - Limits are enforced on the frequency of contact creation requests to prevent abuse.
  - **Technology Used:**
  - Rate limiting is implemented using **FastAPI-Limiter** and **Redis** as a backend for tracking request counts.
- **Setup:**
  - Redis is configured to handle request tracking for rate limiting.
  - The configuration allows for flexible and scalable enforcement of limits.
- **User Avatar Upload**:
- **Functionality**:
  - Users can upload and update their profile avatars via **Cloudinary**.
  - Avatars are securely stored and accessible via unique URLs provided by Cloudinary.

- **Key Features**:
  - Supports image formats such as **JPEG** and **PNG**.
  - Avatar URLs are saved in the database and linked to the user’s profile.
  - Users can replace their avatar at any time.

- **Workflow**:
  1. Users upload an avatar through a **POST** request to the `/api/users/avatar` endpoint.
  2. The API validates the image and uploads it to Cloudinary.
  3. The generated URL is stored in the database.
  
- **CORS (Cross-Origin Resource Sharing)**:
  - Enabled to allow secure API access from web-based clients.
- **Functionality**:
  - CORS is enabled to allow secure access to the API from web-based clients hosted on different domains.
  - It ensures that only authorized origins can interact with the API.

- **Key Features**:
  - Configured to allow requests from specific domains, such as `http://localhost:8000`.
  - Supports credentials for secure cross-origin requests.
  - Allows all HTTP methods (GET, POST, PUT, DELETE) and headers required by the API.

- **Technology Used**:
  - Implemented using FastAPI's **CORSMiddleware**.

- **Example Workflow**:
  1. A client hosted on `http://localhost:8000` sends a request to the API.
  2. The API validates the origin of the request.
  3. If the origin is allowed, the API responds with the requested data.
  4. If the origin is not allowed, the API returns a `403 Forbidden` status.

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
- **Redis**: For implementing rate limiting and caching.

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
  - **Endpoint**: `POST /api/users/avatar`
- **Description**: Upload or update the user’s profile avatar.
- **Functionality**:
  - Users can upload an image (JPEG or PNG) as their avatar.
  - The avatar is securely stored on Cloudinary.
  - A unique URL for the uploaded avatar is saved in the database and linked to the user’s profile.
- **Parameters**:
  - **file** (required): The image file to upload (JPEG or PNG).
- **Response**:
  - **Success**:
    ```json
    {
      "url": "https://res.cloudinary.com/example/image/upload/v12345/avatar.png",
      "public_id": "avatar_12345"
    }
    ```
  - **Error**:
    - `HTTP 400 Bad Request`: If the file format is invalid or another error occurs.
    ```json
    {
      "detail": "Invalid file type. Only JPEG and PNG are allowed."
    }
    ```

### Additional functions
- **Photo search**
- **Endpoint**: `GET /api/photos/search`
- **Description**: Search for photos by keywords in the description, tags, rating, or creation date.

- **Functionality**:
  - Users can search for photos using the following criteria:
    - Keywords in the description.
    - Specific tags.
    - Rating range (e.g., photos with a rating of 4+).
    - Date range for photo creation.

- **Parameters**:
  - **description** (optional): A keyword or phrase to search in the photo description.
  - **tags** (optional): A list of tags to filter photos (comma-separated, e.g., `nature,sunset`).
  - **rating_min** (optional): The minimum rating of the photos.
  - **rating_max** (optional): The maximum rating of the photos.
  - **created_from** (optional): The start date for filtering photos by creation date (format: `YYYY-MM-DD`).
  - **created_to** (optional): The end date for filtering photos by creation date (format: `YYYY-MM-DD`).

- **Response**:
  - **Success**:
    ```json
    [
      {
        "id": 1,
        "url": "https://res.cloudinary.com/example/image/upload/photo1.png",
        "description": "A beautiful sunset",
        "tags": ["sunset", "nature"],
        "rating": 4.5,
        "created_at": "2025-01-01T12:00:00Z"
      },
      {
        "id": 2,
        "url": "https://res.cloudinary.com/example/image/upload/photo2.png",
        "description": "A snowy mountain",
        "tags": ["mountain", "snow"],
        "rating": 5,
        "created_at": "2025-01-02T15:00:00Z"
      }
    ]
    ```
  - **Error**:
    - `HTTP 404 Not Found`: If no photos match the search criteria.
    ```json
    {
      "detail": "No photos found for the given search criteria."
    }
    ```

- **Example Workflow**:
  1. A user sends a `GET` request to the `/api/photos/search` endpoint.
  2. The request includes query parameters (e.g., `tags=nature,sunset&rating_min=4`).
  3. The API filters photos based on the provided criteria.
  4. The filtered photos are returned in the response, or an error is returned if no photos are found.

- **Photo search by author**
- `GET /api/photos/search/{user_id}`
- Search for photos by photo author: by user ID and by username.
- **Description**: Retrieve all photos uploaded by a specific author using their unique user ID or username.
- **Functionality**:
  - Allows users to search for photos by a particular author.
  - Returns a list of photos along with metadata such as description, tags, and rating.
- **Parameters**:
  - **user_id** (required): The unique ID of the user whose photos are being searched.
  - **username** (optional): The username of the author (if implemented in the API).
- **Response**:
  - **Success**:
    ```json
    [
      {
        "photo_id": 101,
        "author_id": 5,
        "author_username": "john_doe",
        "photo_url": "https://cloudinary.com/example/photo1.jpg",
        "description": "Sunrise by the beach",
        "tags": ["sunrise", "beach", "nature"],
        "rating": 4.7
      },
      {
        "photo_id": 102,
        "author_id": 5,
        "author_username": "john_doe",
        "photo_url": "https://cloudinary.com/example/photo2.jpg",
        "description": "City skyline at night",
        "tags": ["city", "skyline", "night"],
        "rating": 4.9
      }
    ]
    ```
  - **Error**:
    - `HTTP 404 Not Found`: If no photos are found for the specified user ID or username.
    ```json
    {
      "detail": "No photos found for the specified author."
    }
    ```
- **Example Workflow**:
  1. A user sends a `GET` request to `/api/photos/search/{user_id}` with the `user_id` of the author.
  2. The API retrieves all photos uploaded by the specified user.
  3. The API returns a list of photos, each including details such as `photo_id`, `photo_url`, `description`, `tags`, and `rating`.

# Transforms a Photo

## Endpoint
`GET /api/photos/{photo_id}/transform`

## Description
Transforms a photo by applying various modifications such as resizing, cropping, rotating, and adding effects. This feature is highly customizable, allowing users to adjust the appearance of their images for specific use cases.

---

## Parameters
- **photo_id** (required): The ID of the photo to transform.
- **width** (optional): Specifies the desired width (in pixels) of the transformed image.
- **height** (optional): Specifies the desired height (in pixels) of the transformed image.
- **crop** (optional): Crop mode for the image. Possible values:
  - `fill` (default): Fills the dimensions, possibly cropping the image.
  - `scale`: Scales the image proportionally.
  - `fit`: Fits the image within the specified dimensions while maintaining its aspect ratio.
- **angle** (optional): Rotates the image by the specified number of degrees (e.g., `90`, `180`, `270`).
- **effect** (optional): Applies a specific visual effect to the image. Supported effects include:
  - `grayscale`: Converts the image to black-and-white.
  - `sepia`: Adds a vintage warm-tone effect.
  - `blur`: Blurs the image to soften details.
  - `sharpen`: Enhances the sharpness of the image.
  - `invert`: Inverts the colors of the image.
- **quality** (optional): Sets the quality of the output image. Acceptable values range from `1` (lowest quality) to `100` (highest quality). Default is `80`.
- **format** (optional): Specifies the output format of the transformed image. Supported formats include:
  - `jpeg`
  - `png`
  - `webp`
- **background** (optional): Sets a background color for images with transparency (e.g., `white`, `black`, or a HEX color like `#FFFFFF`).
- **aspect_ratio** (optional): Adjusts the aspect ratio of the image (e.g., `1:1` for square images, `16:9` for widescreen).
- **brightness** (optional): Adjusts the brightness of the image. Positive values increase brightness, while negative values decrease it.
- **contrast** (optional): Adjusts the contrast of the image. Positive values increase contrast, while negative values decrease it.

---

## Workflow
1. **Request**: A user sends a `GET` request to the `/photos/{photo_id}/transform` endpoint with the desired transformation parameters as query parameters.
2. **Processing**: The API retrieves the photo, applies the requested transformations, and saves the transformed image to the cloud.
3. **Response**: The API returns a URL for the transformed image, which the user can view or download.

---

## Example Request
```http
GET /api/photos/123/transform?width=400&height=400&crop=fill&effect=sepia&angle=90&quality=80&format=jpeg

- **Photo rating**
- `PUT /api/photos/{photo_id}/rating`
- Rate a photo from 0 to 5. Calculates the photo rating - the average value of all likes. The rating value for unrated photos is Null.
- You can rate a photo only once. You cannot rate your own photo.
- **Endpoint**: `PUT /api/photos/{photo_id}/rating`
- **Description**: Allows users to rate a photo between 0 and 5. The rating is calculated as the average of all ratings provided by different users.
- **Functionality**:
  - Users can submit a single rating for a photo.
  - A user cannot rate their own photo.
  - Updates the photo's average rating in the database.
- **Parameters**:
  - **photo_id** (required): The ID of the photo to be rated.
  - **rating** (required): The rating value (between 0 and 5).
- **Response**:
  - **Success**:
    ```json
    {
      "photo_id": 123,
      "average_rating": 4.6,
      "total_ratings": 15
    }
    ```
  - **Error**:
    - `HTTP 403 Forbidden`: If the user attempts to rate their own photo.
    ```json
    {
      "detail": "You cannot rate your own photo."
    }
    ```
    - `HTTP 400 Bad Request`: If the rating value is invalid (e.g., out of range).
    ```json
    {
      "detail": "Invalid rating value. Ratings must be between 0 and 5."
    }
    ```

---

- **View all likes for a photo**
- **Endpoint**: `GET /api/photos/{photo_id}/rating`
- **Description**: Retrieve all likes (ratings) associated with a specific photo by its ID. 
- **Functionality**:
  - Returns detailed information about all likes for the photo, including the users who rated it and their ratings.
  - Access is restricted to moderators and administrators for moderation purposes.
- **Parameters**:
  - **photo_id** (required): The unique ID of the photo for which to retrieve ratings.
- **Response**:
  - **Success**:
    ```json
    {
      "photo_id": 123,
      "likes": [
        {
          "user_id": 1,
          "rating": 5
        },
        {
          "user_id": 2,
          "rating": 4
        }
      ]
    }
    ```
  - **Error**:
    - `HTTP 403 Forbidden`: If a regular user attempts to access this endpoint.
    ```json
    {
      "detail": "Access denied. Only moderators and administrators are allowed."
    }
    ```
    - `HTTP 404 Not Found`: If the photo with the specified ID does not exist.
    ```json
    {
      "detail": "Photo not found."
    }
    ```



- **Delete likes for a photo**
- **Endpoint**: `DELETE /api/photos/rating/{like_id}`
- **Description**: Delete a specific like (rating) associated with a photo by its unique like ID.
- **Functionality**:
  - Allows moderators and administrators to remove inappropriate or invalid likes from a photo.
  - Ensures moderation and control over photo ratings.
- **Parameters**:
  - **like_id** (required): The unique ID of the like to delete.
- **Access**:
  - Only moderators and administrators are authorized to access this endpoint.
- **Response**:
  - **Success**:
    ```json
    {
      "message": "Like has been successfully deleted."
    }
    ```
  - **Error**:
    - `HTTP 403 Forbidden`: If a regular user attempts to access this endpoint.
    ```json
    {
      "detail": "Access denied. Only moderators and administrators are allowed."
    }
    ```
    - `HTTP 404 Not Found`: If the like with the specified ID does not exist.
    ```json
    {
      "detail": "Like not found."
    }
    ```

### **Comment Management**

- **Functionality**:
  - Users can add comments under photos to provide feedback or engage in discussions.
  - Comments can be edited by their authors but cannot be deleted by them.
  - Moderators and administrators can delete any comments.
  - Each comment includes timestamps for when it was created and last updated.

- **Key Features**:
  - Supports the addition of comments to photos.
  - Allows authors to update their comments.
  - Moderators and administrators have permission to delete inappropriate or unwanted comments.
  - Stores the creation and update timestamps for each comment in the database for better traceability.

- **Endpoints**:
  - **Add a Comment**:
    - **Endpoint**: `POST /api/comments/`
    - **Description**: Add a new comment to a specific photo.
    - **Parameters**:
      - **photo_id** (required): The ID of the photo being commented on.
      - **text** (required): The content of the comment.
    - **Response**:
      - **Success**:
        ```json
        {
          "id": 1,
          "photo_id": 101,
          "author_id": 5,
          "text": "Amazing photo!",
          "created_at": "2025-01-07T12:00:00Z",
          "updated_at": "2025-01-07T12:00:00Z"
        }
        ```
      - **Error**:
        - `HTTP 404 Not Found`: If the specified photo does not exist.
        - `HTTP 400 Bad Request`: If required fields are missing.

  - **Get Comments for a Photo**:
    - **Endpoint**: `GET /api/comments/{photo_id}`
    - **Description**: Retrieve all comments for a specific photo.
    - **Parameters**:
      - **photo_id** (required): The ID of the photo for which comments are requested.
    - **Response**:
      - **Success**:
        ```json
        [
          {
            "id": 1,
            "photo_id": 101,
            "author_id": 5,
            "text": "Amazing photo!",
            "created_at": "2025-01-07T12:00:00Z",
            "updated_at": "2025-01-07T12:00:00Z"
          },
          {
            "id": 2,
            "photo_id": 101,
            "author_id": 6,
            "text": "Beautiful composition!",
            "created_at": "2025-01-07T13:00:00Z",
            "updated_at": "2025-01-07T13:00:00Z"
          }
        ]
        ```
      - **Error**:
        - `HTTP 404 Not Found`: If the specified photo does not exist.

  - **Edit a Comment**:
    - **Endpoint**: `PUT /api/comments/{comment_id}`
    - **Description**: Update the text of an existing comment.
    - **Parameters**:
      - **comment_id** (required): The ID of the comment to update.
      - **text** (required): The new content of the comment.
    - **Response**:
      - **Success**:
        ```json
        {
          "id": 1,
          "photo_id": 101,
          "author_id": 5,
          "text": "Updated comment text.",
          "created_at": "2025-01-07T12:00:00Z",
          "updated_at": "2025-01-07T14:00:00Z"
        }
        ```
      - **Error**:
        - `HTTP 403 Forbidden`: If the user is not the author of the comment.
        - `HTTP 404 Not Found`: If the specified comment does not exist.

  - **Delete a Comment**:
    - **Endpoint**: `DELETE /api/comments/{comment_id}`
    - **Description**: Delete a specific comment.
    - **Access**: Only moderators and administrators can delete comments.
    - **Parameters**:
      - **comment_id** (required): The ID of the comment to delete.
    - **Response**:
      - **Success**:
        ```json
        {
          "message": "Comment deleted successfully."
        }
        ```
      - **Error**:
        - `HTTP 403 Forbidden`: If the user does not have permission to delete the comment.
        - `HTTP 404 Not Found`: If the specified comment does not exist.

## Authentication & Authorization
The project includes authentication and authorization mechanisms to restrict access to registered users only.

- **User registration**
 - **Functionality**:
  - Allows users to create new accounts by providing their email, password, and other details.
- **Key Features**:
  - The system checks for duplicate emails to prevent multiple accounts with the same email.
  - Passwords are securely hashed before being stored in the database to ensure security.
  - Upon successful registration:
    - The server responds with `HTTP 201 Created`.
    - The response includes the user’s details, excluding sensitive information like the hashed password.
  - If the email is already registered:
    - The server returns `HTTP 409 Conflict`.
- **Example Response**:
  - **Successful Registration**:
    ```json
    {
      "id": 1,
      "email": "example@example.com",
      "username": "exampleUser",
      "role": "user"
    }
    ```
  - **Duplicate Email**:
    ```json
    {
      "detail": "Account already exists"
    }
    ```

- **Email Verification**
  - **Functionality**:
  - Requires users to verify their email address to activate their accounts.
- **Key Features**:
  - Upon registration, users receive a verification email containing a secure token.
  - The token is embedded in a link that the user clicks to confirm their email.
  - The email includes:
    - A personalized greeting.
    - A link generated dynamically with a limited validity period.
  - Unverified accounts cannot access the API.
- **Example Workflow**:
  1. The user registers and receives a verification email.
  2. The user clicks the verification link, which directs them to the `/api/auth/confirmed_email/{token}` endpoint.
  3. The server validates the token and confirms the email.
  4. The user gains access to the API.
- **Example Responses**:
  - **Email Verified**:
    ```json
    {
      "message": "Email confirmed"
    }
    ```
  - **Verification Error**:
    ```json
    {
      "detail": "Verification error"
    }
    ```

- **Login and JWT Tokens**
  - **Functionality**:
  - Authenticates users by validating their email and password.
  - Issues secure tokens for authenticated users.
- **Key Features**:
  - Users provide their email and password to log in.
  - If credentials are invalid:
    - The server returns `HTTP 401 Unauthorized`.
  - Upon successful authentication:
    - The server generates and returns:
      - **Access Token**: Grants short-term access to protected resources.
      - **Refresh Token**: Allows renewing the access token without re-authenticating.
    - Tokens are securely signed and include expiration times.
- **Example Workflow**:
  1. The user sends a `POST` request to `/api/auth/login` with their credentials.
  2. The server validates the credentials and issues the tokens.
  3. The user includes the `access_token` in the headers for subsequent requests.
- **Example Responses**:
  - **Successful Login**:
    ```json
    {
      "access_token": "eyJhbGciOiJIUzI1...",
      "refresh_token": "eyJhbGciOiJIUzI1...",
      "token_type": "bearer"
    }
    ```
  - **Invalid Credentials**:
    ```json
    {
      "detail": "Invalid email or password"
    }
    ```

- **Access Restrictions**
 - **Functionality**:
  - Restricts users from accessing or modifying content that does not belong to them.
- **Key Features**:
  - Users can only access and modify their own contacts, photos, and other resources.
  - Role-based access control ensures:
    - Regular users can manage their content.
    - Moderators can manage user-generated content (e.g., delete inappropriate comments).
    - Administrators have full access to all content and management features.
  - All POST operations return `HTTP 201 Created` on success.
- **Security Measures**:
  - Tokens are validated on each request to ensure the user’s session is active.
  - Unauthorized actions return an `HTTP 403 Forbidden` or `HTTP 401 Unauthorized` status.

  ## Running Tests
     The project includes comprehensive automated tests to verify the functionality and reliability of the API, service layer, and database interactions. Follow these steps to run the tests:
  ## Prerequisites
	  1.	Ensure that the application dependencies are installed by   running: pip install -r requirements.txt
    2.	If using Docker, make sure your database and Redis services are running: docker-compose up -d
  ## Run All Tests 
    To execute all the tests in the project, use the following command: pytest -v
    This command will discover and run all test files in the tests directory.

 ## Run Tests for Specific Modules
   If you want to test specific modules, use the appropriate test files:
  1.	Authentication Tests: pytest -v tests/test_auth.py
   •	Includes tests for user signup, login, email verification, and   token generation.
  2.	Photo Management Tests: pytest -v tests/test_photos.py
   •	Covers photo upload, delete, update, and search functionalities.
  3.	Comment Management Tests: pytest -v tests/test_comments.py
   •	Tests for adding, retrieving, updating, and deleting comments.
  4.	Service Layer Tests: pytest -v tests/test_services.py
   •	Verifies the functionality of cloud services, rating calculations, and image transformations.
  5.	User Management Tests: pytest -v tests/test_users.py
	 • Includes tests for user profile updates, avatar uploads, and   email confirmation.

## Service Layer Testing

   The service layer includes functionality such as photo rating calculation, cloud uploads, and image transformations. Key tests include:
 #	Photo Rating Calculation:
	    •	Ensures the correct calculation of average photo ratings.
	    •	Verifies database query execution for likes and ratings.
 # Cloudinary Upload:
	   •	Simulates uploading images to Cloudinary and handles success/failure scenarios.
	   •	Validates the file type and ensures proper exceptions are raised for unsupported formats.
 # Image Transformation:
	   •	Tests the generation of transformed image URLs with valid/invalid parameters.
## Running Tests
     The project includes comprehensive automated tests to verify the functionality and reliability of the API, service layer, and database interactions. Follow these steps to run the tests:
  ## Prerequisites
	  1.	Ensure that the application dependencies are installed by   running: pip install -r requirements.txt
    2.	If using Docker, make sure your database and Redis services are running: docker-compose up -d
  ## Run All Tests 
    To execute all the tests in the project, use the following command: pytest -v
    This command will discover and run all test files in the tests directory.

 ## Run Tests for Specific Modules
   If you want to test specific modules, use the appropriate test files:
  1.	Authentication Tests: pytest -v tests/test_auth.py
   •	Includes tests for user signup, login, email verification, and   token generation.
  2.	Photo Management Tests: pytest -v tests/test_photos.py
   •	Covers photo upload, delete, update, and search functionalities.
  3.	Comment Management Tests: pytest -v tests/test_comments.py
   •	Tests for adding, retrieving, updating, and deleting comments.
  4.	Service Layer Tests: pytest -v tests/test_services.py
   •	Verifies the functionality of cloud services, rating calculations, and image transformations.
  5.	User Management Tests: pytest -v tests/test_users.py
	 • Includes tests for user profile updates, avatar uploads, and   email confirmation.

## Service Layer Testing

   The service layer includes functionality such as photo rating calculation, cloud uploads, and image transformations. Key tests include:
 #	Photo Rating Calculation:
	    •	Ensures the correct calculation of average photo ratings.
	    •	Verifies database query execution for likes and ratings.
 # Cloudinary Upload:
	   •	Simulates uploading images to Cloudinary and handles success/failure scenarios.
	   •	Validates the file type and ensures proper exceptions are raised for unsupported formats.
 # Image Transformation:
	   •	Tests the generation of transformed image URLs with valid/invalid parameters.
 ## Running Tests
     The project includes comprehensive automated tests to verify the functionality and reliability of the API, service layer, and database interactions. Follow these steps to run the tests:
  ## Prerequisites
	  1.	Ensure that the application dependencies are installed by   running: pip install -r requirements.txt
    2.	If using Docker, make sure your database and Redis services are running: docker-compose up -d
  ## Run All Tests 
    To execute all the tests in the project, use the following command: pytest -v
    This command will discover and run all test files in the tests directory.

 ## Run Tests for Specific Modules
   If you want to test specific modules, use the appropriate test files:
  1.	Authentication Tests: pytest -v tests/test_auth.py
   •	Includes tests for user signup, login, email verification, and   token generation.
  2.	Photo Management Tests: pytest -v tests/test_photos.py
   •	Covers photo upload, delete, update, and search functionalities.
  3.	Comment Management Tests: pytest -v tests/test_comments.py
   •	Tests for adding, retrieving, updating, and deleting comments.
  4.	Service Layer Tests: pytest -v tests/test_services.py
   •	Verifies the functionality of cloud services, rating calculations, and image transformations.
  5.	User Management Tests: pytest -v tests/test_users.py
	 • Includes tests for user profile updates, avatar uploads, and   email confirmation.

## Service Layer Testing

   The service layer includes functionality such as photo rating calculation, cloud uploads, and image transformations. Key tests include:
 #	Photo Rating Calculation:
	    •	Ensures the correct calculation of average photo ratings.
	    •	Verifies database query execution for likes and ratings.
 # Cloudinary Upload:
	   •	Simulates uploading images to Cloudinary and handles success/failure scenarios.
	   •	Validates the file type and ensures proper exceptions are raised for unsupported formats.
 # Image Transformation:
	   •	Tests the generation of transformed image URLs with valid/invalid parameters.
## Running Tests
     The project includes comprehensive automated tests to verify the functionality and reliability of the API, service layer, and database interactions. Follow these steps to run the tests:
  ## Prerequisites
	  1.	Ensure that the application dependencies are installed by   running: pip install -r requirements.txt
    2.	If using Docker, make sure your database and Redis services are running: docker-compose up -d
  ## Run All Tests 
    To execute all the tests in the project, use the following command: pytest -v
    This command will discover and run all test files in the tests directory.

 ## Run Tests for Specific Modules
   If you want to test specific modules, use the appropriate test files:
  1.	Authentication Tests: pytest -v tests/test_auth.py
   •	Includes tests for user signup, login, email verification, and   token generation.
  2.	Photo Management Tests: pytest -v tests/test_photos.py
   •	Covers photo upload, delete, update, and search functionalities.
  3.	Comment Management Tests: pytest -v tests/test_comments.py
   •	Tests for adding, retrieving, updating, and deleting comments.
  4.	Service Layer Tests: pytest -v tests/test_services.py
   •	Verifies the functionality of cloud services, rating calculations, and image transformations.
  5.	User Management Tests: pytest -v tests/test_users.py
	 • Includes tests for user profile updates, avatar uploads, and   email confirmation.

## Service Layer Testing

   The service layer includes functionality such as photo rating calculation, cloud uploads, and image transformations. Key tests include:
 #	Photo Rating Calculation:
	    •	Ensures the correct calculation of average photo ratings.
	    •	Verifies database query execution for likes and ratings.
 # Cloudinary Upload:
	   •	Simulates uploading images to Cloudinary and handles success/failure scenarios.
	   •	Validates the file type and ensures proper exceptions are raised for unsupported formats.
 # Image Transformation:
	   •	Tests the generation of transformed image URLs with valid/invalid parameters.

## View Test Results
  After running the tests, you can view the results in your terminal or generate detailed reports. Below are the steps to view and interpret the test results:
1.	Basic Test Results:
	•	After running pytest -v, the test results will appear in the terminal.
	•	Each test case will show its status:
	•	PASSED: The test case passed successfully.
	•	FAILED: The test case failed, and the reason will be displayed.
	•	SKIPPED: The test case was skipped (e.g., if marked with @pytest.mark.skip).
#	Example Output:
================================== test session starts ===================================
collected 25 items                                                                        

tests/test_auth.py::test_signup PASSED                                                   [  4%]
tests/test_auth.py::test_login PASSED                                                    [  8%]
tests/test_photos.py::test_upload_photo PASSED                                           [ 12%]
tests/test_comments.py::test_add_comment PASSED                                          [ 16%]
tests/test_services.py::test_rating_calculation PASSED                                   [ 20%]

=================================== 25 passed in 3.45s ==================================

2.	Detailed Results:
	 •	To view detailed information about failed tests, you can add 
   the  -v (verbose) flag: pytest -v
   •	If a test fails, you will see:
	 •	The name of the test case.
	 •	The file and line number where the error occurred.
	 •	A traceback of the error.

3.	Generate a Test Coverage Report (Optional):
	 •	To measure how much of your code is covered by the tests, use the pytest-cov plugin: pytest --cov=src --cov-report=term-missing
   •	This will show:
	 •	Which lines of code were executed during the tests.
	 •	Lines that are missing test coverage.

    #	Example Output:
-------------------------- coverage: platform linux, python 3.10 --------------------------
Name                                      Stmts   Miss  Cover   Missing
---------------------------------------------------------------------
src/entity/models.py                       100     10    90%   55-60
src/routes/auth.py                          50      5    95%   32-35
src/repository/photos.py                   200     15    92%   120-140
---------------------------------------------------------------------
TOTAL                                      350     30    91%

4.	Debugging Failed Tests:
	•	If a test fails, you can re-run just that specific test using: pytest tests/test_auth.py::test_signup
  •	Add the -s flag to see the standard output or debug messages during the test execution: pytest -s tests/test_auth.py

5.	Generate an HTML Test Report (Optional):
	 • To generate an HTML report for easier visualization, install the pytest-html plugin: pip install pytest-html
   •	Run tests with the HTML report option: pytest --html=report.html
   	•	Open the report.html file in your browser to view a detailed test report.

By following these steps, you can effectively view, analyze, and debug your test results for the project.

## Deployment

This application is deployed on the **Koyeb** platform. You can access the live version of the API, including its Swagger documentation, via the following link:

[PhotoShare API Deployment](https://photoshare-rest-api.koyeb.app/docs#/)

Koyeb is a developer-friendly serverless platform to deploy apps globally. It simplifies deployment with no need for managing servers or infrastructure.

## General Requirements
- The project is built with FastAPI.
- Uses SQLAlchemy ORM to interact with the PostgreSQL database.
- Includes full CRUD functionality for managing contacts.
- Authentication and authorization using JWT tokens.
- Supports data validation through Pydantic.
- Exposes API documentation through FastAPI built-in Swagger interface.
- Rate limiting is applied to restrict request frequency.
- CORS is enabled to control cross-origin requests.
- Docker Compose is used for managing services, including the database and API.

## License
This project is licensed under the MIT License - see the LICENSE file for details.

---
