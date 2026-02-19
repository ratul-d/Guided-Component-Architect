from typing_extensions import TypedDict

class GraphState(TypedDict):
    user_prompt: str
    css_framework: str

    previous_code: str | None

    generated_code: str | None
    validation_errors: list[str] | None
    is_valid: bool | None

    retry_count: int
    max_retries: int

    final_code: str | None