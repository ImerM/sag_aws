NAME=spades
TAG=3.13.1

all: build push

build:
	docker build -t $(NAME):$(TAG) -t $(NAME):latest -f Dockerfile --build-arg VERSION=$(TAG) ../..
	docker tag $(NAME):$(TAG) $(REGISTRY):$(TAG)
	docker tag $(NAME):latest $(REGISTRY):latest

push:
	docker push $(REGISTRY):$(TAG)
	docker push $(REGISTRY):latest