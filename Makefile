clean:
	-docker rm `docker ps -a -q`
	-docker rmi `docker images -q --filter "dangling=true"`
	-docker network prune -f

images: clean
	docker build -t willnx/vlab-proxy .
