# IPyFIXweb - Network Analyser (IPFIX and PCAP compatible)

What is IPyFIXweb ?
What are the use cases and problems that it solve ?
What are the components and how they work ?

- [Objectives](#objectives)
- [Working Features](#working-features)
- [Roadmap](#roadmap)
- [Run application container](#run-application-conatiner)

## Objectives

## Working Features

## Roadmap

## Run application conatiner

>**Build container image (docker or podman):**

    podman build . -t ipyfix/web

![container_size](/docs/ipyfixweb_project/images/build_image.png)

>**Run container (docker or podman):**

    podman run -d --name ipyfix-web-dev -p 8001:8000 ipyfix/web

![container](/docs/ipyfixweb_project/images/app_container.png)

---

* [*Basic Examples*](/docs/examples/README.md)

* [*Development info and details*](/docs/ipyfixweb_project/architecture/README.md)