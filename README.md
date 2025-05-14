
# RTK Provisioning API

## Стек
- FastAPI
- RabbitMQ (aio-pika)
- Docker + Compose
- Worker (асинхронная обработка задач)
- In-memory store

## Быстрый старт

```bash
make up
```

## Тестирование

```bash
make test
```

## Отправка задачи

```bash
curl -X POST http://localhost:8000/api/v1/equipment/cpe/TEST123
```

## Проверка статуса

```bash
curl http://localhost:8000/api/v1/equipment/cpe/TEST123/task/<task_id>
```
