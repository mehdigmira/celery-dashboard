docker_celery3:
	sudo docker build --build-arg celery_version=3.1 -t celery3_dashboard_local .

docker_celery4:
	sudo docker build --build-arg celery_version=4.1 -t celery4_dashboard_local .

test2_celery3: docker_celery3
	sh -c "sudo docker run --rm -i -t -p 6379:6379 -p 5555:5555 -p 5431:5432 -v `pwd`:/app:Z -w /app celery3_dashboard_local python2.7 -m pytest tests/ -svx"

test2_celery4: docker_celery4
	sh -c "sudo docker run --rm -i -t -p 6379:6379 -p 5555:5555 -p 5431:5432 -v `pwd`:/app:Z -w /app celery4_dashboard_local python2.7 -m pytest tests/ -svx"

test3_celery3: docker_celery3
	sh -c "sudo docker run --rm -i -t -p 6379:6379 -p 5555:5555 -p 5431:5432 -v `pwd`:/app:Z -w /app celery3_dashboard_local python3 -m pytest tests/ -svx"

test3_celery4: docker_celery4
	sh -c "sudo docker run --rm -i -t -p 6379:6379 -p 5555:5555 -p 5431:5432 -v `pwd`:/app:Z -w /app celery4_dashboard_local python3 -m pytest tests/ -svx"

shell_celery3: docker_celery3
	sh -c "sudo docker run --rm -i -t -p 6379:6379 -p 5555:5555 -p 5431:5432 -v `pwd`:/app:Z -w /app celery3_dashboard_local bash"

shell_celery4: docker_celery4
	sh -c "sudo docker run --rm -i -t -p 6379:6379 -p 5555:5555 -p 5431:5432 -v `pwd`:/app:Z -w /app celery4_dashboard_local bash"