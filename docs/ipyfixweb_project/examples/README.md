***Basic test 1:***

The web-api adapter, the web-server startup (asyncio app "entry" loop) and main are tested.

    http://localhost:8000/api/v1/test/health

***Basic test 2:***

The app and the entire architecture was successfully tested. The route: **/api/v1/test/time_series/{uuid}/info** tested the **adapter, port/interfaces and app's core services/uses-cases** fully decoupled with dependency inversion.

    http://localhost:8000/api/v1/test/time_series/1164a4ac-1415-4316-a455-1f8d650348b2/info

>**Testing output**

![Testing](/docs/ipyfixweb_project/images/starting_tests.png)