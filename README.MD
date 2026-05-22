# 🚀 JTS Backend Project

Welcome to the JTS Backend Project README!

## 📁 Project Structure

```
.
├── README.MD
├── oltp_finance.py
├── oltp_main.py
├── oltp_purchasing.py
├── requirements.txt
├── src
│   ├── __init__.py
│   ├── core
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── dependencies.py
│   │   └── security.py
│   ├── infra
│   │   ├── powerbi
│   │   │   ├── __init__.py
│   │   │   ├── client.py
│   │   │   └── route.py
│   │   └── upload
│   │       ├── __init__.py
│   │       ├── client.py
│   │       ├── repository.py
│   │       ├── route.py
│   │       ├── schema.py
│   │       └── service.py
│   ├── main.py
│   ├── models
│   │   ├── __init__.py
│   │   ├── finance.py
│   │   ├── models.py
│   │   ├── models_export.py
│   │   └── stg_table.py
│   ├── modules
│   │   ├── departments
│   │   │   ├── __init__.py
│   │   │   ├── registry.py
│   │   │   ├── repository.py
│   │   │   ├── route.py
│   │   │   ├── schema.py
│   │   │   └── service.py
│   │   ├── history
│   │   │   ├── __init__.py
│   │   │   ├── repository.py
│   │   │   ├── route.py
│   │   │   ├── schema.py
│   │   │   └── service.py
│   │   ├── roles
│   │   │   ├── __init__.py
│   │   │   ├── repository.py
│   │   │   ├── route.py
│   │   │   ├── schema.py
│   │   │   └── service.py
│   │   ├── transaction
│   │   │   ├── __init__.py
│   │   │   ├── repository.py
│   │   │   ├── router.py
│   │   │   ├── schema.py
│   │   │   └── service.py
│   │   └── users
│   │       ├── __init__.py
│   │       ├── repository.py
│   │       ├── route.py
│   │       ├── schema.py
│   │       └── service.py
│   ├── seed.py
│   └── workers
│       ├── celery_app.py
│       ├── cleaning
│       │   ├── __init__.py
│       │   ├── abstract_cleaning.py
│       │   ├── base_cleaning_service.py
│       │   ├── finance_service.py
│       │   ├── purchasing_service.py
│       │   ├── sales_service.py
│       │   ├── service_factory.py
│       │   └── tasks.py
│       ├── cleanser
│       │   ├── __init__.py
│       │   ├── finance.py
│       │   ├── purchase.py
│       │   ├── purchasing.py
│       │   └── sales.py
│       ├── mappers
│       │   ├── finance.py
│       │   ├── purchasing.py
│       │   └── sales.py
│       ├── queries
│       │   ├── __init__.py
│       │   ├── finance.py
│       │   ├── purchasing.py
│       │   └── sales.py
│       └── transformers
│           └── __init__.py
├── src.models.models.py
└── stg_table.py
```

## ▶️ How to Run

### Celery

To run Celery in development mode:
1.  Change directory to your project dashboard:
    ```bash
    cd ~/jts-project/project-dashboard
    ```
2.  Start the Celery worker:
    ```bash
    celery -A src.workers.celery_app worker --loglevel=info
    ```

### FastAPI

To run FastAPI in development mode:
1.  Change directory to your project dashboard:
    ```bash
    cd ~/jts-project/project-dashboard
    ```
2.  Start the FastAPI server:
    ```bash
    uvicorn src.main:app --host 0.0.0.0 --port 8881 --reload
    ```

### Celery with PM2

To run Celery using PM2 for production environments:
1.  Change directory to your project dashboard:
    ```bash
    cd ~/jts-project/project-dashboard
    ```
2.  Start Celery with PM2:
    ```bash
    pm2 start "celery -A config.celery_conf --loglevel=info" --name prod-worker
    ```

### FastAPI with PM2

To run FastAPI using PM2 for production environments:
1.  Change directory to your project dashboard:
    ```bash
    cd ~/jts-project/project-dashboard
    ```
2.  Start FastAPI with PM2:
    ```bash
    pm2 start "uvicorn main:app --host 0.0.0.0 --port 8000" --name prod-be
    ```