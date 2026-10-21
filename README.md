
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

### 3.1 Architecture Overview

TaskFlow follows a microservices-based architecture. The application is divided into two independent application services and a MongoDB database.

Each microservice has a specific responsibility and communicates with other services through REST APIs.

The application runs in Docker containers and is deployed using Kubernetes.

### 3.2 Architecture Diagram

```text
                  +----------------------+
                  |     Web Browser      |
                  |   TaskFlow Dashboard |
                  +----------+-----------+
                             |
                             | HTTP Requests
                             v
                  +----------------------+
                  |     Task Service     |
                  |   Flask REST API     |
                  |      Port 5002       |
                  +----------+-----------+
                             |
                 +-----------+-----------+
                 |                       |
                 | MongoDB               | HTTP REST
                 | Connection            | Request
                 v                       v
        +------------------+   +----------------------+
        |     MongoDB      |   |  Statistics Service  |
        |    Port 27017    |   |    Flask REST API    |
        |                  |   |      Port 5001       |
        +------------------+   +----------+-----------+
                                          |
                                          | GET /api/tasks
                                          v
                                   Task Service
```

The browser communicates with the Task Service, which provides the user interface and task management functionality.

When statistics are requested, the Task Service forwards the request to the Statistics Service. The Statistics Service retrieves task information through the Task Service REST API and calculates the statistics.

### 3.3 Software Components and Responsibilities

**Task Service**

The Task Service manages task-related operations.

Its responsibilities include:
- Creating, retrieving, updating and deleting tasks.
- Providing REST API endpoints.
- Communicating with MongoDB.
- Serving the browser-based dashboard.
- Forwarding statistics requests to the Statistics Service.

**Statistics Service**

The Statistics Service handles calculations related to task progress.

Its responsibilities include:
- Retrieving tasks through the Task Service REST API.
- Counting tasks based on their status.
- Calculating the completion percentage.
- Returning calculated statistics as JSON.

**MongoDB**

MongoDB stores the application's task data.

It runs separately from the application services and uses persistent storage in Kubernetes.

### 3.4 Mapping Software Components to Microservices

| Software Component | Implementation | Deployment |
|-------------------|----------------|------------|
| User interface | HTML, CSS, JavaScript | Task Service |
| Task management | Python Flask | Task Service |
| Statistics calculation | Python Flask | Statistics Service |
| Data storage | MongoDB | MongoDB StatefulSet |

Each application microservice has its own Docker image and Kubernetes Deployment.

MongoDB is deployed separately using a StatefulSet.

### 3.5 Architecture Design Principles

**Separation of Responsibilities**

Each microservice focuses on a specific function.

The Task Service manages task information, while the Statistics Service calculates statistics.

**REST-Based Communication**

The microservices communicate through HTTP REST APIs.

The Statistics Service retrieves task information from the Task Service rather than connecting directly to MongoDB.

This keeps database access within the Task Service.

**Independent Deployment and Scaling**

Both application microservices have separate Kubernetes Deployments.

This allows them to be deployed and scaled independently.

For example, additional Statistics Service replicas can be introduced without increasing the number of Task Service replicas.

**Containerization**

Docker packages each microservice with its application code and dependencies.

This provides a consistent execution environment across Docker Compose and Kubernetes.

**Persistent Storage**

MongoDB uses a Kubernetes PersistentVolumeClaim to retain task data when its pod is recreated.

### 3.6 Architecture Decisions and Trade-offs

**Why Microservices?**

Microservices allow different application responsibilities to be separated.

This improves modularity and demonstrates independent deployment and scaling.

However, microservices also introduce additional networking, configuration and operational complexity compared with a single application.

**Why REST APIs?**

REST APIs provide a simple and widely supported communication method.

They allow the Statistics Service to retrieve task information without accessing the database directly.

However, synchronous REST communication creates dependencies between services.

**Why Kubernetes?**

Kubernetes manages container deployment, service discovery, scaling and health monitoring.

It also supports persistent storage and resource management.

For a small application like TaskFlow, Kubernetes introduces more complexity than is strictly necessary. It is used here to demonstrate cloud-native deployment principles.

**Why MongoDB?**

MongoDB stores task information as documents, which fits the structure of the task data.

The application uses a single MongoDB instance because database scaling is not required for this project.

### 3.7 Current Architecture Limitations

The current dashboard statistics request follows this sequence:

1. The browser requests statistics from the Task Service.
2. The Task Service calls the Statistics Service.
3. The Statistics Service calls the Task Service to retrieve tasks.
4. The Task Service retrieves data from MongoDB.
5. The Statistics Service calculates the results and returns them.

This creates a circular synchronous request dependency.

During development, the Task Service initially used a single synchronous Gunicorn worker, causing statistics requests to time out.

The issue was resolved by configuring Gunicorn with two workers and four threads per worker.

For a larger production application, an API gateway or a different communication design could reduce this dependency.

The application is intentionally small. Independent horizontal scaling is demonstrated as a technical capability rather than a current business necessity.

### 3.8 Benefits, Challenges and Security Considerations

#### Benefits of the Architecture

**Independent Development and Deployment**

TaskFlow separates task management and statistics calculations into two microservices.

This makes it possible to update or deploy one service without necessarily changing the other.

**Independent Scaling**

Kubernetes allows the Task Service and Statistics Service to scale independently.

For example, if statistics calculations become more demanding, additional Statistics Service replicas can be deployed without scaling the entire application.

In the current project, the workload is small, so scaling is demonstrated mainly to show the technical capability.

**Maintainability**

Each microservice has a clearly defined responsibility.

This makes the code easier to understand, test and maintain compared with having all functionality in one large application.

**Portability**

Docker packages the application and its dependencies into containers.

The same application can run using Docker Compose or Kubernetes, reducing differences between development and deployment environments.

**Reliability**

Kubernetes readiness and liveness probes help detect unhealthy application containers.

Persistent MongoDB storage also ensures that task data can survive database pod recreation.

#### Challenges and Mitigation

**1. Communication Between Microservices**

TaskFlow uses synchronous REST communication.

The Statistics Service depends on the Task Service to retrieve task information.

During development, a circular request dependency caused HTTP 503 errors when the Task Service used a single synchronous Gunicorn worker.

Mitigation:
- Configured Gunicorn with two workers and four threads per worker.
- Added request timeouts and error handling.
- Used Kubernetes Service names for internal communication.

For a larger system, an API gateway or redesigned communication flow could reduce these dependencies.

**2. Increased Deployment Complexity**

Microservices require separate Docker images, Kubernetes Deployments, Services and environment configurations.

Mitigation:
- Used Docker Compose for local development.
- Used Kubernetes YAML files for repeatable deployments.
- Documented deployment commands in the README.

**3. Database Availability**

The Task Service depends on MongoDB.

If MongoDB becomes unavailable, task management operations may fail.

Mitigation:
- Used a Kubernetes StatefulSet.
- Configured persistent storage.
- Verified that task data survives MongoDB pod recreation.

Persistent storage protects against pod recreation but does not replace database backups or high availability.

**4. Resource Consumption**

Multiple containers require more resources than a simple standalone application.

Mitigation:
- Configured CPU and memory requests and limits.
- Used lightweight Python container images.
- Kept the application deployment small.

#### Security Considerations

Both application microservices use Kubernetes security settings:

- Run as non-root user 10001.
- Prevent privilege escalation.
- Drop unnecessary Linux capabilities.
- Use the RuntimeDefault seccomp profile.

These settings reduce the privileges available to application containers.

However, the application still has security limitations:

- MongoDB authentication is not configured.
- Users are not required to authenticate.
- Internal REST communication does not use TLS.
- Kubernetes NetworkPolicies are not configured.
- Automated security scanning is not implemented.

For production use, these limitations should be addressed through authentication, encrypted communication, network restrictions, secrets management and security scanning.

#### Business Implications

A microservices architecture can provide business value when different application components have different workloads or development requirements.

Independent scaling can reduce unnecessary resource consumption when only one service needs additional capacity.

Independent deployment can also allow teams to release changes without redeploying the entire application.

However, microservices introduce additional operational costs related to networking, monitoring, deployment and maintenance.

For a small application like TaskFlow, a monolithic architecture would probably be simpler and less expensive.

Microservices were selected primarily to demonstrate cloud-native architecture principles, rather than because the current workload requires them.


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
