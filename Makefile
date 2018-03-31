docker:
	sudo docker build -t celery_dashboard_local .

test: docker
	sh -c "sudo docker run --rm -i -t -p 6379:6379 -p 5555:5555 -p 5432:5432 -v `pwd`:/app:rw -w /app celery_dashboard_local python -m pytest tests/ -v --instafail"

test3: docker
	sh -c "sudo docker run --rm -i -t -p 6379:6379 -p 5555:5555 -p 5432:5432 -v `pwd`:/app:rw -w /app celery_dashboard_local python3 -m pytest tests/ -v --instafail"

shell: docker
	sh -c "sudo docker run --rm -i -t -p 6379:6379 -p 5555:5555 -p 5431:5432 -v `pwd`:/app:Z -w /app celery_dashboard_local bash"