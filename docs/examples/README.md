***Basic test 1:***

The main, the web-api adapter, the web-server startup (asyncio loop) are tested.

    http://localhost:8000/api/v1/test/health

***Basic test 2:***

The app and the entire architecture was successfully tested. **The async route: /api/v1/test/time_series/{uuid}** tested the **async adapter (RRDtool filesystem), port/interfaces and app's core services/uses-cases** fully decoupled with dependency inversion.

    http://localhost:8000/api/v1/test/time_series/264c3408-aec2-59fb-9712-f2f5a555d982

![Testing2](/docs/ipyfixweb_project/images/tests2.png)

    http://localhost:8000/api/v1/test/time_series/1164a4ac-1415-4316-a455-1f8d650348b2

![Testing](/docs/ipyfixweb_project/images/tests.png)
