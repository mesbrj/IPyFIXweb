# Summary

> ## Application CMD (main, startup)
>
> **Web_api adapters** completely decoupled from **app's CMDs**.
> Select what web-framework to start or changing the adapter (to CLI for
example) are possible.
>
> ## Ports/Interfaces (in use this moment)
>
> **Core app_services/use_cases** completely decoupled using dependency
inversion from the **infrastructure and related adapters**:
>
>- **Repositories** *interfaces/ports (ipfix, pcap, sql, time_series)*
>**Where they are defined ?**
>*src/ports/repositories*
>**Where they are implemented ?**
>*src/adapters/infrastructure*
>**Where they are used ?**
>*src/use_cases (business)*
>
> **Adapter web_api** completely decoupled using dependency inversion from
**Core app_services/use_cases**
>
>- **Imput** *interfaces/ports (analysis, commands, queries)*
>**Where they are defined ?**
>*src/ports/imput*
>**Where they are implemented ?**
>*src/use_cases (service)*
>**Where they are used ?**
>*src/adapters/web_api/[framework-web]/controllers*
