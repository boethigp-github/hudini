from locust import HttpUser, task, events
from locust.runners import MasterRunner, WorkerRunner, LocalRunner
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_test_users(environment, msg):
    # Example setup logic
    logger.info("Setting up test users")
    # You can initialize test users here, e.g., by making requests to your FastAPI application

class ModelsUser(HttpUser):
    host = "http://localhost:8000"  # Replace with your FastAPI server's address

    @task
    def get_models(self):
        with self.client.get("/models", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
                logger.info("Request succeeded with status 200")
            else:
                response.failure(f"Got unexpected status code: {response.status_code}")
                logger.error(f"Request failed with status code: {response.status_code}")

    def on_start(self):
        # Optional: Perform any setup actions (e.g., authentication) here
        pass

# Event listener to set up the custom message handler
@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    if isinstance(environment.runner, MasterRunner) or isinstance(environment.runner, WorkerRunner):
        # Register the custom message handler on the runner
        environment.runner.register_message('test_users', setup_test_users, concurrent=True)
        logger.info("Custom message handler registered")

# Main block to run the test script
if __name__ == "__main__":
    # Create a local runner (single machine)
    runner = LocalRunner(env=None)

    # Optionally: Start the web UI for monitoring
    web_ui = runner.start_web_ui("127.0.0.1", 8089)

    # Register the custom message handler (if not done in `on_test_start`)
    if isinstance(runner, MasterRunner) or isinstance(runner, WorkerRunner):
        runner.register_message('test_users', setup_test_users, concurrent=True)
        logger.info("Custom message handler registered in main block")

    # Start the test
    logger.info("Starting the test")
    runner.start(1, spawn_rate=1)
    runner.greenlet.join()

    # Stop the web UI after the test
    if web_ui:
        web_ui.stop()
        logger.info("Web UI stopped")
