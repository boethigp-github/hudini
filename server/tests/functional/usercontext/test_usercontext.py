import unittest
import random
import string
import uuid
import requests
from fastapi.encoders import jsonable_encoder
from datetime import datetime
from server.app.models.usercontext.usercontext_post_request_model import UserContextPostRequestModel, ContextDataItem
from server.app.models.usercontext.usercontext_post_request_model import UserContextPrompt
from server.app.config.settings import Settings
from server.app.models.users.users_post_request import UserPostRequestModel

class TestUserContext(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Initialize the settings
        cls.settings = Settings()
        cls.BASE_URL = cls.settings.get("default").get("SERVER_URL")

        # Get the first user UUID or create a test user
        cls.test_user_uuid = cls.get_first_user_uuid()

    @classmethod
    def get_first_user_uuid(cls):
        """Fetch the first user from the database or create a new test user."""
        response = requests.get(f"{cls.BASE_URL}/users")
        if response.status_code != 200:
            raise AssertionError(f"Failed to fetch users: {response.text}")

        users = response.json()
        if users:
            return str(users[0]['uuid'])  # Use the UUID of the first user as a string
        else:
            return cls.create_test_user()

    @classmethod
    def generate_random_string(cls, length=10):
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

    @classmethod
    def create_test_user(cls):
        """Create a test user if none exists."""
        username = cls.generate_random_string()
        email = f"{cls.generate_random_string()}@example.com"
        create_payload = UserPostRequestModel(
            username=username,
            email=email
        )
        response = requests.post(f"{cls.BASE_URL}/users", json=create_payload.model_dump())  # Updated from dict()
        if response.status_code != 201:
            raise AssertionError(f"Failed to create test user: {response.text}")
        return response.json().get('uuid')

    def create_test_prompt_data(self):
        """
        Creates test data for the prompt object using UserContextPrompt.
        """
        return UserContextPrompt(
            uuid=str(uuid.uuid4()),  # Convert UUID to string
            prompt="Test prompt",
            user=self.test_user_uuid,  # Use test user's UUID
            status="IN_PROGRESS",
            context_data=[  # Realistic context data
                ContextDataItem(
                    id=uuid.uuid4(),  # Generate a UUID for context item
                    user=self.test_user_uuid,  # Use test user UUID
                    status="COMPLETED",  # Example status
                    model="TestModel",  # Example model
                    completion={
                        "id": str(uuid.uuid4()),  # Completion ID
                        "choices": [
                            {
                                "index": 0,
                                "message": {
                                    "content": "Test completion message",
                                    "role": "assistant"
                                }
                            }
                        ]
                    }
                ).model_dump()  # Convert context data to dict
            ]
        ).model_dump()  # Updated from dict()

    def create_user_context(self, thread_id, context_data_list, prompt_data_list):
        """
        Creates multiple user contexts with the provided thread_id, context_data, and prompt_data.
        Uses the test user UUID created in setUpClass.
        """
        user_contexts = []
        for prompt_data, context_data in zip(prompt_data_list, context_data_list):
            payload = UserContextPostRequestModel(
                uuid=str(uuid.uuid4()),  # Generate a new UUID for the context
                user=self.test_user_uuid,  # Use the test user UUID
                thread_id=thread_id,
                prompt=UserContextPrompt(**prompt_data),  # Prompt data passed correctly as UserContextPrompt
                context_data=context_data  # Add the context data
            )
            user_contexts.append(payload.model_dump())  # Updated from dict()

        # Ensure proper encoding of UUIDs using jsonable_encoder
        payload_list = jsonable_encoder(user_contexts)

        response = requests.post(f"{self.BASE_URL}/usercontext", json=payload_list)
        if response.status_code != 200:
            print(f"Create User Context Response: {response.text}")  # Debugging output
        self.assertEqual(response.status_code, 200)
        return response.json()

    def test_create_and_get_user_contexts(self):
        # Create test prompt data
        prompt_data_list = [self.create_test_prompt_data() for _ in range(2)]  # Create two sets of prompt data

        # Context and thread setup
        thread_id = 1
        context_data_list = [
            [
                ContextDataItem(
                    id=uuid.uuid4(),  # Generate a new UUID for the context item
                    user=self.test_user_uuid,  # UUID for the user
                    status="IN_PROGRESS",
                    model="TestModel",
                    completion={"id": str(uuid.uuid4()),
                                "choices": [{"index": 0, "message": {"content": "Test message", "role": "assistant"}}]}
                ).model_dump()  # Updated from dict()
            ] for _ in range(2)  # Create context data for two different user contexts
        ]

        # Log and validate the user context creation process
        try:
            created_contexts = self.create_user_context(thread_id, context_data_list, prompt_data_list)

            # Retrieve user contexts by thread_id and user
            response = requests.get(f"{self.BASE_URL}/usercontext",
                                    params={"thread_id": thread_id, "user": self.test_user_uuid})
            self.assertEqual(response.status_code, 200)
            contexts = response.json()

            # Validate that the context data and prompt are correct for multiple contexts
            for idx, context in enumerate(contexts):
                self.assertEqual(context["user"], created_contexts[idx]["user"])
                self.assertEqual(context["prompt"]["uuid"], prompt_data_list[idx]["uuid"])

        except AssertionError as e:
            print(f"Unexpected status code: {e}")

    def test_export_user_context_to_excel(self):
        # Test case for exporting user context to Excel
        thread_id = 1

        # Create test user context first
        prompt_data_list = [self.create_test_prompt_data() for _ in range(1)]  # Create a single prompt
        context_data_list = [
            [
                ContextDataItem(
                    id=uuid.uuid4(),
                    user=self.test_user_uuid,
                    status="IN_PROGRESS",
                    model="TestModel",
                    completion={"id": str(uuid.uuid4()),
                                "choices": [{"index": 0, "message": {"content": "Test message", "role": "assistant"}}]}
                ).model_dump()
            ]
        ]

        # Create the user context
        created_context = self.create_user_context(thread_id, context_data_list, prompt_data_list)

        try:
            # Ensure the user context has been created in the database before proceeding
            # Retry fetching the context until it's available or timeout (retry mechanism)
            for _ in range(5):  # Retry up to 5 times
                response = requests.get(f"{self.BASE_URL}/usercontext",
                                        params={"thread_id": thread_id, "user": self.test_user_uuid})
                if response.status_code == 200 and len(response.json()) > 0:
                    break  # Data is now available
                else:
                    time.sleep(1)  # Wait a second before retrying

            # Perform the Excel export after ensuring the data is available
            export_response = requests.get(f"{self.BASE_URL}/usercontext/export/excel",
                                           params={"thread_id": thread_id, "user": self.test_user_uuid})

            self.assertEqual(export_response.status_code, 200)
            self.assertEqual(export_response.headers["Content-Disposition"],
                             'attachment; filename=user_context_export.xlsx')

            # Validate if the response content type is Excel
            self.assertEqual(export_response.headers["Content-Type"],
                             "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

            # Check the content of the Excel file (optional validation)
            from io import BytesIO
            import openpyxl

            # Load the Excel content from the response
            excel_content = BytesIO(export_response.content)
            workbook = openpyxl.load_workbook(excel_content)
            sheet = workbook.active

            # Validate the headers
            headers = [cell.value for cell in sheet[1]]
            self.assertEqual(headers, ["UUID", "User", "Thread ID", "Context Data", "Created", "Updated"])

            # Validate that the created prompt is present in the Excel data
            prompt_found = False
            for row in sheet.iter_rows(min_row=2, values_only=True):
                if row[0] == created_context[0]["uuid"]:  # Compare UUID of the created context
                    prompt_found = True
                    self.assertEqual(row[1], self.test_user_uuid)  # Check if the user matches
                    self.assertEqual(row[2], thread_id)  # Check if the thread_id matches
                    self.assertIn("Test completion message", row[3])  # Check if context_data contains the message
                    break

            self.assertTrue(prompt_found, "The created prompt was not found in the exported Excel file.")

        finally:
            # Clean up by deleting the created user context after the test
            delete_response = requests.delete(f"{self.BASE_URL}/usercontext/{thread_id}")
            self.assertEqual(delete_response.status_code, 200)
            print(f"User context with thread_id {thread_id} successfully deleted.")


if __name__ == '__main__':
    unittest.main()
