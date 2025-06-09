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
    - [Development environment](#development-environment)
      - [Pre-requirements to run the application](#pre-requirements-to-run-the-application)

## Objectives

## Roadmap

## Development info and details

### Hexagonal Architecture

>**Diagram**

![architecture_hexagonal](/docs/architecture/hexagonal_architecture.png)

>**Repo directory tree**

![dir_tree](/docs/architecture/final_hexagonal_marked._dir_tree.png)

### Development environment

#### Pre-requirements to run the application

> *... This section needs to be improved urgently ...*
>
>**Install Pre-reqs**
>For RPM distros (Fedora/RHEL/Oracle-Linux):
>
>- Development Tools group packages, perl-CPAN, pango-devel, libxml2-devel, rrdtool-devel
>
>*Please, see the **Dockerfile** for some glues on APT distros.*
>
>Create (or use) one python virtual environment.
>Install python requirimets (inside root repo directory):

    pip install -r requirements.txt

*inside root repo directory, run:*

    python src/cmd/main.py

***Basic test 1:***

    http://localhost:8000/api/v1/test/health

***Basic test 2:***

    http://localhost:8000/api/v1/test/time_series/1164a4ac-1415-4316-a455-1f8d650348b2/info

>**Testing output**

![Testing](/docs/examples/starting_tests.png)
