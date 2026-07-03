# Risk Copilot AWS Deployment Lab

A portfolio project documenting the containerization and AWS deployment design of a **FastAPI-based risk analytics application**, using a production-style architecture with **Docker, Amazon ECR, Amazon ECS Fargate, Application Load Balancer, AWS Secrets Manager, and CloudWatch Logs**.

This project began as an **AWS App Runner** deployment exercise, but was later redesigned to use **ECS Fargate** after identifying service-access and account-tier limitations. The revised solution provides stronger exposure to core AWS infrastructure concepts such as container orchestration, secure secret injection, networking, health checks, and service-level deployment.

---

## Overview

The goal of this lab was to take a Python web application and prepare it for deployment in a realistic AWS container environment.

The work included:

- containerizing the application with Docker
- preparing container image publishing to Amazon ECR
- designing runtime secret handling with AWS Secrets Manager
- replacing an App Runner approach with an ECS Fargate architecture
- planning load-balanced deployment using an Application Load Balancer
- configuring logging and health-check patterns for operational visibility

This project is intended as a hands-on infrastructure and deployment exercise rather than a feature-heavy application build.

---

## Objectives

- Deploy a containerized FastAPI application on AWS
- Use managed AWS services where practical
- Avoid hardcoding credentials in source code or image layers
- Follow a production-style deployment flow
- Build hands-on familiarity with AWS services relevant to modern backend/cloud engineering

---

## Tech Stack

### Application
- Python
- FastAPI
- Uvicorn

### Containerization
- Docker

### AWS Services
- Amazon ECR
- Amazon ECS
- AWS Fargate
- Application Load Balancer
- AWS Secrets Manager
- Amazon CloudWatch Logs
- IAM
- VPC / Security Groups

---

## Project Structure

Example structure:

```text
.
├── app/
│   ├── api/
│   │   └── main.py
│   ├── core/
│   ├── services/
│   └── ...
├── Dockerfile
├── requirements.txt
├── README.md
└── ...
```

Adjust this section to match the actual structure of your repository.

---

## Architecture

The target deployment architecture is:

```text
User
  ↓
Application Load Balancer (HTTP)
  ↓
Amazon ECS Service (Fargate)
  ↓
FastAPI container
  ↓
Amazon ECR image
  ↓
Secrets injected from AWS Secrets Manager
  ↓
Logs written to Amazon CloudWatch Logs
```

### Key components

- **Amazon ECR** stores the Docker image
- **ECS Fargate** runs the container without managing EC2 servers
- **Application Load Balancer** exposes the service publicly and routes traffic to the container
- **Secrets Manager** stores sensitive configuration such as API keys
- **CloudWatch Logs** captures container stdout/stderr for troubleshooting
- **IAM roles** allow ECS to pull images, read secrets, and push logs securely

---

## Why ECS Instead of App Runner

The original plan was to deploy this application through **AWS App Runner** for simplicity. During setup, I found that App Runner was not the best fit under the current AWS account constraints and free-plan limitations.

I therefore redesigned the deployment to use **Amazon ECS Fargate**, which offered two advantages:

1. it avoided blocking progress on a service-access issue
2. it provided stronger learning value in core AWS deployment concepts

From a portfolio perspective, the ECS version is also more valuable because it covers:

- container orchestration
- task definitions and services
- IAM execution roles
- load balancer integration
- health checks
- security groups
- operational logging

---

## Setup

## 1. Clone the repository

```bash
git clone <your-repo-url>
cd <your-project-folder>
```

---

## 2. Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

On Windows:

```bash
.venv\Scripts\activate
```

---

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Configure environment variables

Create a local environment file such as `.env` if needed.

Example:

```env
POE_API_KEY=your_api_key_here
POE_BASE_URL=https://api.poe.com/v1
POE_MODEL=gpt-5.4
```

For AWS deployment, sensitive values should not be stored in `.env` inside the production environment. Instead, store secrets in **AWS Secrets Manager** and inject them into the ECS task at runtime.

---

## 5. Run locally

Example local run command:

```bash
uvicorn app.api.main:app --host 0.0.0.0 --port 8000
```

Test locally:

```text
http://localhost:8000/api/health
http://localhost:8000/dashboard
```

---

## Docker Setup

## 1. Build the image

```bash
docker build -t risk-copilot .
```

---

## 2. Run the container locally

```bash
docker run -p 8000:8000 risk-copilot
```

The application must bind to:

- `0.0.0.0`
- port `8000`

Example container command:

```dockerfile
CMD ["uvicorn", "app.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## AWS Deployment

## Prerequisites

Before deployment, make sure you have:

- an AWS account with sufficient service access
- AWS CLI configured
- Docker installed
- an ECR repository created
- required secrets stored in AWS Secrets Manager
- permission to create ECS, IAM, ALB, and CloudWatch resources

---

## 1. Authenticate Docker to Amazon ECR

Example:

```bash
aws ecr get-login-password --region <your-region> | \
docker login --username AWS --password-stdin <your-account-id>.dkr.ecr.<your-region>.amazonaws.com
```

Replace:
- `<your-region>`
- `<your-account-id>`

---

## 2. Tag the image

```bash
docker tag risk-copilot:latest <your-account-id>.dkr.ecr.<your-region>.amazonaws.com/risk-copilot:latest
```

---

## 3. Push the image to ECR

```bash
docker push <your-account-id>.dkr.ecr.<your-region>.amazonaws.com/risk-copilot:latest
```

---

## 4. Create a CloudWatch log group

```bash
aws logs create-log-group --log-group-name /ecs/risk-copilot
```

---

## 5. Create an ECS cluster

```bash
aws ecs create-cluster --cluster-name risk-copilot-cluster
```

---

## 6. Create IAM roles

For ECS deployment, the task execution role should allow:

- pulling images from ECR
- writing logs to CloudWatch
- reading secrets from Secrets Manager

At minimum, attach:

- `AmazonECSTaskExecutionRolePolicy`

Then add an inline policy allowing:

- `secretsmanager:GetSecretValue`

for the required secret ARN.

---

## 7. Create an ECS task definition

The task definition should include:

- **launch type**: Fargate
- **OS**: Linux
- **CPU / memory**: e.g. `0.5 vCPU`, `1 GB`
- **image URI** from ECR
- **container port**: `8000`
- environment variables for non-sensitive config
- secret injection for sensitive config
- CloudWatch log configuration

Example values:

- task family: `risk-copilot-task`
- container name: `risk-copilot`
- log group: `/ecs/risk-copilot`
- health endpoint: `/api/health`

---

## 8. Create security groups

### ALB security group
Allow inbound:
- HTTP `80` from `0.0.0.0/0`

### ECS task security group
Allow inbound:
- TCP `8000`
- source: ALB security group only

This keeps the container private behind the load balancer.

---

## 9. Create an Application Load Balancer

Recommended settings:

- internet-facing
- at least 2 public subnets
- listener: HTTP `80`

Create a target group with:

- target type: `IP`
- protocol: HTTP
- port: `8000`
- health check path: `/api/health`

---

## 10. Create the ECS service

Recommended settings:

- launch type: Fargate
- desired tasks: `1`
- attach the ECS task definition
- connect the service to the ALB target group
- use the ECS task security group
- configure subnets in the selected VPC

Once created, ECS will launch the task, pull the container from ECR, inject secrets, and register the task behind the load balancer.

---

## 11. Validate deployment

After the service is running, retrieve the ALB DNS name and test:

```text
http://<alb-dns-name>/api/health
http://<alb-dns-name>/dashboard
```

---

## Runtime Configuration

This project separates configuration into:

### Non-sensitive configuration
Passed as normal environment variables, for example:

- `POE_BASE_URL`
- `POE_MODEL`

### Sensitive configuration
Stored in **AWS Secrets Manager** and injected into the ECS task at runtime, for example:

- `POE_API_KEY`

This avoids embedding secrets in:
- source code
- Git history
- Docker image layers

---

## Observability

### Logging
Container logs are sent to:

- **Amazon CloudWatch Logs**
- log group: `/ecs/risk-copilot`

This supports debugging for:
- startup failures
- dependency issues
- missing environment variables
- runtime exceptions

### Health checks
The deployment uses:

- ALB target group health checks
- application endpoint: `/api/health`

This allows ECS/ALB to determine whether the container is healthy and routable.

---

## Troubleshooting

Common issues and checks:

### 1. ECS task stops immediately
Check:
- ECS task stop reason
- CloudWatch logs
- import/runtime errors
- missing environment variables

### 2. Target group shows unhealthy
Check:
- health check path is correct
- container is listening on `0.0.0.0:8000`
- application returns HTTP 200 for `/api/health`

### 3. ECS cannot pull image
Check:
- image exists in ECR
- image URI is correct
- task execution role has ECR permissions

### 4. Secret injection fails
Check:
- secret ARN is correct
- execution role has `secretsmanager:GetSecretValue`
- environment variable mapping in task definition is correct

### 5. No logs appear
Check:
- CloudWatch log group exists
- task definition logging is enabled
- execution role has logging permissions

---

## Lessons Learned

This project reinforced several practical lessons:

### 1. Service simplicity does not always mean best fit
Although App Runner looked simpler initially, account and service-tier constraints made it less practical in this case. Switching to ECS Fargate allowed progress to continue and resulted in a stronger infrastructure learning outcome.

### 2. Container deployment is more than just Docker
A working Docker image is only one part of cloud deployment. In practice, a reliable service also needs:
- image registry
- identity and permissions
- secret management
- networking
- routing
- logging
- health checks

### 3. Secret handling should be designed early
It is much cleaner to design secure configuration patterns from the beginning rather than retrofitting them later.

### 4. Operational visibility matters
CloudWatch logs and health checks are essential. They reduce debugging time significantly when containers fail to start or become unhealthy behind a load balancer.

### 5. ECS provides stronger infrastructure learning value
Compared with a more abstract managed deployment service, ECS gave me better exposure to how modern containerized applications are actually wired together in AWS.

---

## Portfolio Value

This project demonstrates hands-on work in:

- Docker containerization
- AWS deployment workflows
- ECS/Fargate architecture
- secure runtime secret management
- load-balanced web service design
- cloud troubleshooting and operational thinking

It complements my broader background in:

- Python implementation
- quantitative/risk systems
- automation and AI-enabled workflows
- production-oriented solution delivery

---

## Current Status

Current progress:
- application prepared for containerized deployment
- ECR workflow prepared
- secret-management pattern defined
- App Runner approach replaced by ECS Fargate architecture
- ECS deployment plan and required resources identified

Next step:
- execute the ECS deployment end-to-end and validate the running service behind the Application Load Balancer

---

## Future Improvements

Potential next enhancements:

- add HTTPS with ACM
- add custom domain routing
- enable autoscaling for ECS service
- add CI/CD pipeline for build and deployment
- add Terraform or CloudFormation for infrastructure as code
- add monitoring/metrics dashboards
- improve security hardening for production deployment

---

## Disclaimer

This repository is primarily a deployment and infrastructure learning project. Some implementation details, names, and service settings may be simplified for lab and portfolio purposes.

---

## Author

**Cheung Chit Wang Felix**  
Quantitative Risk & AI Implementation Analyst
