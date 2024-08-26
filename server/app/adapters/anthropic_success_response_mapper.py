from datetime import datetime
from server.app.models.success_generation_model import SuccessGenerationModel, Completion, Choice, Message, Usage

class AnthropicResponseToSuccessGenerationResponseAdapter:
    @staticmethod
    def map_to_success_response(anthropic_message: dict, model_id: str, prompt_id: str) -> SuccessGenerationModel:
        """
        Maps the raw response from Anthropic API to the SuccessGenerationModel.

        Args:
            anthropic_message (dict): The raw response from the Anthropic API.
            model_id (str): The ID of the model used for this response.
            prompt_id (str) UUID of prompt
        Returns:
            SuccessGenerationModel: The mapped success generation model.
        """

        # Map the choices from content
        choices = [
            Choice(
                finish_reason=anthropic_message.get('stop_reason', ''),
                index=0,  # Assuming a single choice for simplicity
                message=Message(
                    content=content.get('text', 'no-text from response'),
                    role=anthropic_message.get('role')
                )
            )
            for content in anthropic_message.get('content', [])
        ]

        # Map the usage information
        usage_info = anthropic_message.get('usage', {})
        usage = Usage(
            completion_tokens=usage_info.get('output_tokens', 0),
            prompt_tokens=usage_info.get('input_tokens', 0),
            total_tokens=usage_info.get('input_tokens', 0) + usage_info.get('output_tokens', 0)
        )

        # Get the current timestamp
        current_timestamp = int(datetime.now().timestamp())

        # Create and return the SuccessGenerationModel
        return SuccessGenerationModel(
            prompt_id=prompt_id,
            model=anthropic_message.get('model', model_id),
            completion=Completion(
                id=anthropic_message.get('id'),
                choices=choices,
                created=current_timestamp,  # Set current timestamp
                model=anthropic_message.get('model'),
                object=anthropic_message.get('type'),
                usage=usage
            )
        )
