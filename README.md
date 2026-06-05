# 🚀 Distributed Order Fulfillment Engine

An event-driven, production-grade microservices architecture demonstrating distributed transaction management, asynchronous communication, and clean architecture principles.

## 📖 Overview

I built this project to solve a classic distributed systems problem: **How do you guarantee data consistency across multiple independent databases without a central orchestrator?** This application simulates an e-commerce checkout flow. It utilizes the **Saga Pattern (Choreography)** to handle order creation and inventory reservation. By decoupling the services via Apache Kafka and preventing race conditions with Redis distributed locks, the system ensures high availability, eventual consistency, and zero data loss.

---

## 🏗️ System Architecture

graph TD
The project consists of an API Gateway routing traffic to isolated microservices. The services do not communicate via HTTP; instead, they react asynchronously to domain events.

```text
                       +----------------------+
                       | Client / Frontend    |
                       +----------+-----------+
                                  |
                                  v
                       +----------------------+
                       | Nginx API Gateway    |
                       +----------+-----------+
                                  |
                                  v
                       +----------------------+
                       | Order Service API    |
                       +----------+-----------+
                                  |
                      saves PENDING    v
                       +----------------------+
                       | Orders DB (Postgres) |
                       +----------------------+
                                  |
                                  v
                       +----------------------+
                       | Apache Kafka (KRaft) |
                       +----------+-----------+
                                  |
                                  v
                       +----------------------+
                       | Inventory Consumer   |
                       +----------+-----------+
                          |               |
                          | lock          | deducts stock
                          v               v
                   +--------------+   +----------------------+
                   | Redis Cache/ |   | Inventory DB         |
                   | Lock         |   | (Postgres)           |
                   +--------------+   +----------------------+
```

### 🛠️ Tech Stack

- Language: Python 3.11
- Web Framework: Flask (App Factory Pattern)
- Message Broker: Apache Kafka (KRaft mode, no Zookeeper)
- Databases: PostgreSQL (Isolated schemas via SQLAlchemy ORM)
- Caching & Locking: Redis
- Gateway & Proxy: Nginx
- Infrastructure: Docker & Docker Compose (Multi-stage builds)

### 🧩 Microservices Breakdown

1. **Order Service (The Publisher)**
   - Responsibility: Handles customer-facing HTTP requests. Acts as the initiator of the Saga.
   - Flow: Validates the incoming payload, saves the order as `PENDING` in its dedicated Postgres database, and immediately publishes an `OrderCreated` event to Kafka.
   - Architecture: Adheres to Clean/Hexagonal Architecture to strictly separate domain business rules from SQLAlchemy data mappers.

2. **Inventory Service (The Consumer)**
   - Responsibility: Runs entirely in the background listening to the orders Kafka topic.
   - Flow: Consumes events and validates stock. To prevent race conditions during high concurrency, it acquires a distributed lock in Redis for the specific `product_id` before modifying the inventory database.

## 🚦 Getting Started

### Prerequisites
You only need Docker and Docker Compose installed on your machine.

### 1. Boot the Cluster
Clone the repository and spin up the entire multi-container ecosystem using the pre-configured multi-stage Dockerfiles.

```bash
git clone https://github.com/yourusername/ecommerce-fulfillment-engine.git
cd ecommerce-fulfillment-engine
docker-compose up -d --build
```

> Note: Kafka and Postgres take a few seconds to initialize. The Docker Compose file utilizes strict health checks to ensure containers boot in the correct dependency order.

### 2. Initialize the Databases & Seed Data
Because the persistent volumes are fresh, run the infrastructure scripts to create the tables and inject test inventory.

```bash
# Create Order tables
docker exec -it ecommerce_order_service python init_db.py

# Create Inventory tables and seed test products
docker exec -it ecommerce_inventory_consumer python init_db.py
```

## 🧪 Testing the Flow

The system is secured behind the Nginx API Gateway listening on port `8080`.

### The Happy Path (Successful Reservation)
Send an order for a seeded product.

```bash
curl -X POST http://localhost:8080/api/v1/orders/ \
-H "Content-Type: application/json" \
-d '{
  "customer_id": "cust-101",
  "items": [{"product_id": "prod-1", "quantity": 1, "price": 1200.0}]
}'
```

Watch the background consumer logs to confirm it catches the Kafka event, locks the product via Redis, and reserves the stock.

```bash
docker logs ecommerce_inventory_consumer
```

### The Failure Path (Out of Stock)
Attempt to order a quantity that exceeds available inventory.

```bash
curl -X POST http://localhost:8080/api/v1/orders/ \
-H "Content-Type: application/json" \
-d '{
  "customer_id": "cust-102",
  "items": [{"product_id": "prod-1", "quantity": 500, "price": 1200.0}]
}'
```

The consumer logs should show that the business rules caught the deficit, prevented the update, and handled the failure gracefully.

## 📂 Repository Structure

```text
.
├── docker-compose.yml       # Infrastructure state and networking
├── gateway/
│   └── nginx.conf           # Gateway routing and X-Request-ID injection
├── order_service/
│   ├── Dockerfile           # Multi-stage Python build
│   └── src/
│       ├── api/             # HTTP delivery layer (Flask routes)
│       ├── domain/          # Pure Python enterprise business rules
│       ├── infrastructure/  # SQLAlchemy and Kafka producers
│       └── use_cases/       # Application orchestrators
└── inventory_service/
    ├── Dockerfile
    ├── run_consumer.py      # Entry point for the continuous Kafka listener
    └── src/
        ├── domain/
        ├── infrastructure/  # Redis distributed locking and Kafka consumers
        └── use_cases/
```
