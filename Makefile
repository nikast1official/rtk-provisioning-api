
up:
	docker-compose up --build

down:
	docker-compose down -v

restart:
	docker-compose down -v && docker-compose up --build

test:
	pytest tests/
