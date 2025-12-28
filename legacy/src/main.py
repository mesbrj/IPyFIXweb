import asyncio

from cmds.startup import init_app, webapp_startup


if __name__ == "__main__":
    async def main():
        init_app()
        await webapp_startup(workers=3)
    asyncio.run(main())
