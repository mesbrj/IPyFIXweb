import sys, os
sys.path.append(
    os.path.dirname(os.path.dirname(
        os.path.abspath(__file__)))
)
import asyncio
from startup import startup as start_web_server

async def main():
    """
    Main entry point for the application.
    """
    await start_web_server()

if __name__ == "__main__":
    asyncio.run(main())