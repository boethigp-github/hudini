from locust import HttpUser, task, between, events
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PromptUser(HttpUser):
    host = "http://localhost:80"  # Replace with the actual host of your FastAPI server

    @task
    def get_prompts(self):
        with self.client.get("/prompt", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
                logger.info("GET /prompt succeeded with status 200")
            else:
                response.failure(f"GET /prompt failed with status code: {response.status_code}")
                logger.error(f"GET /prompt failed with status code: {response.status_code}")

    # Optional: Perform any setup actions here, if needed
    def on_start(self):
        pass

if __name__ == "__main__":
    import os
    from locust.env import Environment
    from locust.log import setup_logging
    from locust.runners import LocalRunner

    # Set up environment and runner
    setup_logging("INFO", None)
    env = Environment(user_classes=[PromptUser])
    runner = LocalRunner(environment=env)

    # Start the Locust web UI for monitoring
    env.create_web_ui("127.0.0.1", 8089)

    # Start the load test with 10 users, spawning 1 user per second
    runner.start(10, spawn_rate=1)
    runner.greenlet.join()

    # Stop the web UI after the test
    env.web_ui.stop()
