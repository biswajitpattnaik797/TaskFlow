
# TaskFlow – Cloud-Native Task Management Application

## 1. Project Overview

TaskFlow is a cloud-native task management application developed as part of a BTH software engineering assignment.

The application uses a microservices architecture, REST APIs, Docker, Kubernetes and MongoDB.

Users can create, view, update and delete tasks through a browser-based dashboard. The application also provides task statistics, including task counts and completion percentage.

## 2. Technologies Used

- Python 3.13
- Flask
- Gunicorn
- MongoDB 7
- PyMongo
- Requests
- HTML, CSS and JavaScript
- Docker and Docker Compose
- Kubernetes (Minikube)
- Docker Hub
- Git and GitHub

## 3. Application Architecture

TaskFlow consists of two application microservices and one database.

### Task Service

Responsible for:
- Creating tasks
- Retrieving tasks
- Updating task information and status
- Deleting tasks
- Providing the browser-based dashboard
- Forwarding dashboard statistics requests

### Statistics Service

Responsible for:
- Retrieving task information through the Task Service REST API
- Calculating task statistics
- Returning statistics as JSON

### MongoDB

Stores task information persistently.

The Statistics Service does not access MongoDB directly. It communicates with the Task Service through REST APIs.

### Communication Flow

Browser Dashboard
    |
    v
Task Service
    |
    +----> MongoDB
    |
    +----> Statistics Service
                 |
                 +----> Task Service REST API

## 4. REST API Endpoints

### Task Service

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | / | Browser dashboard |
| GET | /api/health | Health check |
| GET | /api/tasks | Retrieve all tasks |
| POST | /api/tasks | Create a task |
| PUT | /api/tasks/{task_id} | Update a task |
| DELETE | /api/tasks/{task_id} | Delete a task |
| GET | /api/dashboard/statistics | Retrieve dashboard statistics |

### Statistics Service

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/statistics | Retrieve calculated task statistics |

## 5. Task Data Structure

Each task contains:

- id
- title
- description
- priority
- status

Supported priorities:
- Low
- Medium
- High

Supported statuses:
- To Do
- In Progress
- Done

Example task:

```json
{
  "title": "Prepare Kubernetes Deployment",
  "description": "Create deployment configurations",
  "priority": "High",
  "status": "To Do"
}
```

## 6. Docker Images

The application microservices are published on Docker Hub.

Task Service:

https://hub.docker.com/r/biswajitpattnaik797/taskflow-task-service

Statistics Service:

https://hub.docker.com/r/biswajitpattnaik797/taskflow-statistics-service

Current application images:

- biswajitpattnaik797/taskflow-task-service:v4
- biswajitpattnaik797/taskflow-statistics-service:v1

## 7. Running with Docker Compose

From the project root directory, run:

```bash
docker compose up -d --build
```

This starts:

- MongoDB
- Task Service
- Statistics Service

Local service addresses:

Task Service:
http://127.0.0.1:5003

Statistics Service:
http://127.0.0.1:5004/api/statistics

To stop the application:

```bash
docker compose down
```

The named MongoDB volume is preserved unless volumes are explicitly removed.

## 8. Kubernetes Deployment

The application was deployed and tested using Minikube.

Start Minikube:

```bash
minikube start
```

Deploy MongoDB:

```bash
kubectl apply -f kubernetes/mongodb.yaml
```

Deploy Task Service:

```bash
kubectl apply -f kubernetes/task-service.yaml
```

Deploy Statistics Service:

```bash
kubectl apply -f kubernetes/statistics-service.yaml
```

Verify the running pods:

```bash
kubectl get pods
```

Access the TaskFlow dashboard:

```bash
kubectl port-forward service/task-service 5009:5002
```

Open:

http://127.0.0.1:5009/

## 9. Horizontal Scaling

Both application microservices can scale independently.

Scale Task Service:

```bash
kubectl scale deployment/task-service --replicas=3
```

Scale Statistics Service:

```bash
kubectl scale deployment/statistics-service --replicas=2
```

Verify scaling:

```bash
kubectl get deployments
kubectl get pods
```

Independent scaling was tested successfully with three Task Service replicas and two Statistics Service replicas.

## 10. Persistent Database Storage

MongoDB runs as a Kubernetes StatefulSet.

A PersistentVolumeClaim provides 1 GiB of storage using ReadWriteOnce access mode.

Persistence was tested by deleting the MongoDB pod:

```bash
kubectl delete pod mongodb-0
```

Kubernetes recreated the pod, and the existing task data remained available.

## 11. Security Configuration

Both application microservices use Kubernetes container security settings:

- Non-root execution using UID 10001
- Non-root group GID 10001
- Privilege escalation disabled
- Linux capabilities dropped
- RuntimeDefault seccomp profile

CPU and memory requests and limits are also configured.

| Resource | Request | Limit |
|----------|---------|-------|
| CPU | 100m | 500m |
| Memory | 128Mi | 512Mi |

MongoDB authentication and additional production security controls are not yet implemented.

### Kubernetes Health Monitoring

Both Task Service and Statistics Service have Kubernetes readiness and liveness probes configured.

- Readiness probes check whether the application is ready to receive requests.
- Liveness probes check whether the application is responding and allow Kubernetes to restart unhealthy containers.
- Both probes use the `/api/health` endpoint.
- Task Service health checks run on port 5002.
- Statistics Service health checks run on port 5001.

Readiness checks run every 10 seconds, while liveness checks run every 20 seconds.

These health endpoints verify HTTP responsiveness but do not check database or downstream service connectivity.

## 12. Testing and Verification

The following functionality has been tested:

- Task creation through REST API
- Task retrieval through REST API
- Task status updates
- Task deletion
- Browser-based task management
- Live task statistics
- Communication between microservices
- Docker container execution
- Docker Compose integration
- Kubernetes deployment
- Independent horizontal scaling
- MongoDB persistence after pod recreation
- Non-root container execution
- REST communication after applying security and resource limits

## 13. Project Structure

```text
TaskFlow/
├── .gitignore
├── README.md
├── docker-compose.yml
├── task-service/
│   ├── app.py
│   ├── Dockerfile
│   ├── requirements.txt
│   └── templates/
│       └── index.html
├── statistics-service/
│   ├── app.py
│   ├── Dockerfile
│   └── requirements.txt
└── kubernetes/
    ├── mongodb.yaml
    ├── task-service.yaml
    └── statistics-service.yaml
```

## 14. Known Limitations

- MongoDB authentication is not yet configured.
- The application does not provide user authentication.
- The dashboard uses a synchronous REST communication pattern between microservices.
- The current deployment is intended for a local learning environment rather than public production use.

## 15. Conclusion

TaskFlow demonstrates the development and deployment of a microservices-based task management application using Docker, Kubernetes and REST APIs.

The project demonstrates independent microservice deployment, horizontal scaling, persistent database storage, browser-based task management and basic container security controls.
