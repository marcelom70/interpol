IMAGE_NAME=interpol-backend
DOCKER_USER=marcelom70
VERSION ?= v1.0  # if omitted, assumes v1.0

FULL_IMAGE_LATEST=$(DOCKER_USER)/$(IMAGE_NAME):latest
FULL_IMAGE_VERSION=$(DOCKER_USER)/$(IMAGE_NAME):$(VERSION)

build:
	docker build --no-cache -t $(IMAGE_NAME) .

tag: build
	docker tag $(IMAGE_NAME) $(FULL_IMAGE_LATEST)
	docker tag $(IMAGE_NAME) $(FULL_IMAGE_VERSION)

login:
	docker login

push: tag
	docker push $(FULL_IMAGE_LATEST)
	docker push $(FULL_IMAGE_VERSION)

deploy: login push
