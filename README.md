# Frappe HR (HRMS)

This project is an open-source Human Resources and Payroll application built on the Frappe framework. It features a complete Python backend and a modern Vue 3 frontend for roster and shift management.

## Project Structure
- `backend/`: The core Python Frappe app handling HR and Payroll logic.
- `roster/`: A Vue.js Single-Page Application (SPA) for interactive Shift Assignment and Roster visualization.
- `docker/`: Contains the Docker environment setup for running the project locally.

## Docker Setup Instructions

This project is fully containerized and uses **PostgreSQL** as the primary database. Follow these steps to get the application running on your local machine:

### Prerequisites
1. [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running.
2. (Windows users) Ensure WSL2 is enabled and integrated with Docker Desktop.

### 1. Start the Containers
Open your terminal and navigate to the `docker` directory, then start the services:

```bash
cd docker
docker-compose up
```
*(Note: You can add `-d` at the end to run it in the background)*

### 2. Automatic Initialization
The first time you start the containers, a script (`init.sh`) will automatically run in the background to:
- Provision the internal PostgreSQL database.
- Create a new Frappe site named `hrms.localhost`.
- Install the HR app onto the site.
- Enable developer mode and background workers.

*Please wait a few minutes for the terminal logs to settle down as the installation completes.*

### 3. Access the Application
Once the setup is finished and the server is running, you can access the application in your browser:

**URL:** [http://hrms.localhost:8000](http://hrms.localhost:8000)

*(Note: Most modern browsers automatically route `.localhost` domains to your local machine. If yours doesn't, simply add `127.0.0.1 hrms.localhost` to your computer's `hosts` file).*

### 4. Default Credentials
Use the following credentials to log in:
- **Username:** `Administrator`
- **Password:** `admin`

### Data Persistence
Your PostgreSQL database files are securely stored inside a Docker Volume (`postgres-data`). This means you can safely stop the containers (`Ctrl+C` or `docker-compose stop`) without losing any of your data!
