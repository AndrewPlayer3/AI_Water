USER_DISPLAY := {$DISPLAY}

.ONESHELL:

.PHONY: container

image: build/AI_Water.Dockerfile
	cd build && \
	xhost + && \
	docker build -f AI_Water.Dockerfile -t ai-water .

container-mac: image
	docker run -it --rm \
		-v ${PWD}:/AI_Water \
		-v ~/.aws:/root/.aws \
		-v ~/Downloads:/root/Downloads \
		--name=AI_Water-dev \
		--workdir="/AI_Water" \
		--net=host \
		-e DISPLAY=host.docker.internal:0 \
		-v ~/Xauthority:/home/user/.Xauthority \
		ai-water:latest \
		bash -c "pip3 install -e . ; bash"

container: image
	docker run -it --rm \
		-v ${PWD}:/AI_Water \
		-v ~/.aws:/root/.aws \
		-v ~/Downloads:/root/Downloads \
		--name=AI_Water-dev \
		--workdir="/AI_Water" \
		--net=host \
		-e DISPLAY \
		-v ~/Xauthority:/home/user/.Xauthority \
		ai-water:latest \
		bash -c "pip3 install -e . ; bash"

test:
	pytest -v --cov-report term-missing --cov=src

test-gui:
	apt-get install x11-apps -y; xeyes

setup-gdal:
	wget http://download.osgeo.org/gdal/2.4.3/gdal-2.4.3.tar.gz && \
	tar -xvzf gdal-2.4.3.tar.gz && \
	./configure --prefix=/usr && \
	make
