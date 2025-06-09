# IPyFIXweb - Modern network analyser (IPFIX and PCAP compatible)

What is IPyFIXweb ? What are the components and how they work ?
...
...
What are the use cases and problems that it solve ?
...
...

## Summary

- [IPyFIXweb - Modern network analyser (IPFIX and PCAP compatible)](#ipyfixweb---modern-network-analyser-ipfix-and-pcap-compatible)
  - [Summary](#summary)
  - [Objectives](#objectives)
  - [Roadmap](#roadmap)
  - [Development info and details](#development-info-and-details)
    - [Hexagonal Architecture](#hexagonal-architecture)
    - [Development environment: Run application conatiner](#development-environment-run-application-conatiner)

## Objectives

## Roadmap

## Development info and details

### Hexagonal Architecture

>**Diagram**

![architecture_hexagonal](/docs/architecture/hexagonal_architecture.png)

>**Repo directory tree**

![dir_tree](/docs/architecture/final_hexagonal_marked._dir_tree.png)

### Development environment: Run application conatiner

Run all commands in the root repo directory.

>**Build container image (docker or podman):**

    podman build . -t ipyfix/web

>**Run container (docker or podman):**

    podman run -d --name ipyfix-web-dev -p 8001:8000 ipyfix/web

![container](/docs/architecture/container.png)
___
***Basic test 1:***

The web-api adapter, the web-server startup (asyncio app "entry" loop) and main are tested.

    http://localhost:8000/api/v1/test/health

***Basic test 2:***

The app and the entire architecture was successfully tested. The route: **/api/v1/test/time_series/{uuid}/info** tested the **adapter, port/interfaces and app's core services/uses-cases** fully decoupled with dependency inversion.

    http://localhost:8000/api/v1/test/time_series/1164a4ac-1415-4316-a455-1f8d650348b2/info

>**Testing output**

![Testing](/docs/examples/starting_tests.png)
