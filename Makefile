clean:
	-rm -rf build
	-rm -rf dist
	-rm -rf *.egg-info
	-rm -f tests/.coverage
	-docker rm `docker ps -a -q`
	-docker rmi `docker images -q --filter "dangling=true"`

build: clean
	python setup.py bdist_wheel --universal

uninstall:
	-pip uninstall -y vlab-api-gateway

install: uninstall build
	pip install -U dist/*.whl

test: uninstall install
	cd tests && nosetests -v --with-coverage --cover-package=vlab_api_gateway

images: build
	docker build -t willnx/vlab-proxy .
	docker build -f GatewayDockerfile -t willnx/vlab-api-gateway .

up:
	docker-compose -p vlabcentos up --abort-on-container-exit
