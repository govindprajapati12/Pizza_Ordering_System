# Project: Pizza Ordering System

This project is a Pizza Ordering System that includes a FastAPI backend, a React frontend, and a PostgreSQL database. The system is containerized using Docker and orchestrated with Docker Compose.

## Features

- **Backend**: FastAPI application running on Python, serving API endpoints for the pizza ordering system.
- **Frontend**: React application served via NGINX.
- **Database**: PostgreSQL for data persistence.
- **Dockerized**: Fully containerized setup for easy deployment.

---

## Prerequisites

- Docker: [Install Docker](https://docs.docker.com/get-docker/)
- Docker Compose: [Install Docker Compose](https://docs.docker.com/compose/install/)

---

## Getting Started

### 1. Clone the Repository
```bash
git clone <repository-url>
cd project
```

### 2. Set Up Environment Variables

Create a `.env` file in the `backend` directory with the following content:
```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=Pizza123
POSTGRES_DB=pizza_db
DATABASE_URL=postgresql://postgres:Pizza123@db:5432/pizza_db
```
For data base migrations
run the command in docker backend terminal 
 step 1:
      alembic init migrations
 step 2:
      alembic revision --autogenerate -m "Initial migration"
 step 3:
      alembic upgrade head


### 3. Build and Run the Containers

Run the following command to build and start the containers:
```bash
docker-compose up --build
```


### 4. Access the Application

- **Frontend**: [http://localhost](http://localhost)
- **Backend API**: [http://localhost:8000](http://localhost:8000)

---

## Services

### 1. Backend
- **Context**: `./backend`
- **Port**: `8000`
- **Environment Variables**: Defined in `./backend/.env`

### 2. Database
- **Image**: PostgreSQL 15
- **Port**: `5442` (mapped to `5432` inside the container)
- **Volumes**: Persistent storage for PostgreSQL data.

### 3. Frontend
- **Context**: `./frontend`
- **Port**: `8080` (mapped to `80` inside the NGINX container)

---

## Development

### Backend
To run the backend locally without Docker:
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend
To run the React app locally:
```bash
cd frontend
npm install
npm start
```

---

## Application Flow

### 1. User Flow

1. Open the application via the web browser.
2. Register as a new user on the **Sign Up** page.
3. Log in using the created credentials.
4. After logging in:
   - Regular users are redirected to the **Home Page**.
   - If additional admin features are needed, use `pgAdmin` to update the user’s role to `admin` in the database.
5. Admin users are automatically redirected to the **Admin Dashboard** upon login.

### 2. Admin Actions

1. In the **Admin Dashboard**, perform the following tasks:
   - Create new pizza or Delete options.
   - Add or Remove available toppings.
   - Create and manage coupons.

### 3. Ordering Process for Normal Users

1. From the **Home Page**, browse and select pizzas.
2. Add desired toppings to your pizza.
3. Add items to the cart.
4. View the **Cart Page**:
   - See the added items and available coupons.
   - Apply a coupon if available.
5. Proceed to **Checkout**:
   - A payment pop-up appears.
   - Enter payment details. If the last digit of the card number is:
     - **Even**: Payment is successful.
     - **Odd**: Payment fails, and the user is redirected back to the **Cart Page**.
6. Upon successful payment:
   - An email confirmation is sent with the order details.
   - The user is redirected to the **Orders Page**.

### 4. Viewing and Managing Orders

1. On the **Orders Page**, users can see all their past orders.
2. Click on an order to view its **Live Status**.
3. Admins can update the status of an order in the **Admin Dashboard**.

---

## Volumes

### `postgres_data2`
Persistent volume used to store PostgreSQL data to ensure data is not lost when the container is restarted.

---
## Troubleshooting

1. **Container Fails to Start**:
   - Check the logs for errors:
     ```bash
     docker-compose logs
     ```

2. **Database Connection Issues**:
   - Verify the environment variables in `./backend/.env`.

3. **Frontend Not Loading**:
   - Ensure the React app is built:
     ```bash
     cd frontend
     npm run build
     ```

---



