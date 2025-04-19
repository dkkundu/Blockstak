# Backend for Blockstak

This is a **FastAPI** project built for the Blockstak. It exposes a set of secure, token-authenticated REST API endpoints and is designed to run both locally (via `uvicorn`) and in a Dockerized environment.

---

## 📦 Project Repo

**GitHub:** [https://github.com/dkkundu/Blockstak.git](https://github.com/dkkundu/Blockstak.git)

---

## 🚀 Project Description

This FastAPI backend service provides a secure, token-based API with 5 endpoints (CRUD operations). It demonstrates proper authentication, environment configuration, Docker usage, and testability. The project is designed to be scalable, secure, and easy to deploy.

---

## ⚙️ Setup Instructions

1. **Clone the Repository**
   ```bash
   git clone https://github.com/dkkundu/Blockstak.git
   cd Blockstak
   ```

2. **Copy Environment File**
   ```bash
   cp example/dot_env .env
   ```

3. **Edit .env File**
   Update the following values in the `.env` file as per your local setup:

   ```env
   PROJECT_NAME="Backend for Blockstak"
   DEBUG=True
   SECRET_KEY=mysecretkey
   WHITE_LIST=http://localhost:8000,http://localhost:9000

   # Database Configuration
   MYSQL_HOST=192.168.55.101
   MYSQL_PORT=3306
   MYSQL_DB=MYSQL_DB_NAME
   MYSQL_USER=MYSQL_USER_NAME
   MYSQL_PASSWORD=MYSQL_USER_PASSWORD

   # API Key
   NEWS_API_KEY=NEWS_API_KEY_form_newsapi.org

   # FastAPI Configuration
   FASTAPI_HOST_PORT=5000
   ```

   Refer to `example/dot_env` for additional guidance if needed.

---

## ▶️ How to Run the Server

### 🔧 Option 1: Using uvicorn (Locally)

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the server:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 9000 --reload
   ```

### 🐳 Option 2: Using Docker

1. Build and run the Docker container:
   ```bash
   docker-compose up --build
   ```

   or

   ```bash
   docker compose up --build
   ```

2. The FastAPI app will be available on the port specified in the `.env` file under `FASTAPI_HOST_PORT`. By default, this is set to `8000`.

---

## 🧪 How to Run Tests


1. Run the tests:
   ```bash
   pytest
   ```

2. View the test coverage report:
   ```bash
   pytest --cov=app
   ```

---

## 🔑 How to Generate Access Tokens and Use Secured Endpoints

1. Use the `/auth/login` endpoint to authenticate and retrieve a JWT token.
2. Include the token in the `Authorization` header for secured endpoints:
   ```http
   Authorization: Bearer <your_token>
   ```

---

## 📡 API Endpoints

This project includes 5 main API endpoints, all documented in the provided Postman collection file.

### 📁 Postman Collection Path:
`example/Blockstak.postman_collection.json`

### ▶️ How to Use the Postman Collection:

1. Open Postman.
2. Go to **File > Import**.
3. Select `example/Blockstak.postman_collection.json`.

---

## 📚 Additional Documentation

- **OpenAPI Docs:** Once the server is running, you can access the auto-generated API documentation at:

- The FastAPI app will be available on the port specified in the `.env` file under `FASTAPI_HOST_PORT`. By default, this is set to `8000`.

  - Swagger UI: [http://localhost:8000/docs](http://localhost:9000/docs)
  - ReDoc: [http://localhost:8000/redoc](http://localhost:9000/redoc)

- **Postman Collection:** Import the Postman collection file located at:
  `example/Blockstak.postman_collection.json`

- **Database Schema:** Add database schema details here if needed.

---

## 👨‍💻 Author

- **Name:** Dipto K Kundu
- **GitHub:** [https://github.com/dkkundu](https://github.com/dkkundu)

---

## 📝 License

This project is licensed for evaluation and demonstration purposes only.

---