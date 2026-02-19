from app.engine.config import llm, design_tokens
from app.engine.state import GraphState
from pydantic import BaseModel, Field
from typing import List

class ValidationResult(BaseModel):
    valid: bool = Field(..., description="Whether the Angular component is valid and compliant")
    errors: List[str] = Field(..., description="List of validation errors if any")


def generate_component(state: GraphState):
    print("Generating Component")

    user_prompt = state["user_prompt"]
    css_framework = state["css_framework"]

    css_rules = ""

    if css_framework == "tailwind":
        css_rules = """
            - Use TailwindCSS utility classes.
            - Use Tailwind syntax for layout and spacing.
            - Do NOT use Angular Material components.
            """
    elif css_framework == "angular-material":
        css_rules = """
            - Use Angular Material components (mat-card, mat-input, mat-button, etc.).
            - Do NOT use Tailwind classes.
            - Import necessary Angular Material modules.
            """
    else:
        css_rules = """
            - Use plain CSS in the styles array.
            - Do NOT use Tailwind or Angular Material.
            """

    system_prompt = f"""
        You are a senior Angular 17 engineer.
        
        Generate a complete Angular standalone component.
        
        STRICT RULES:
        - Return ONLY raw Angular code.
        - Do NOT wrap in markdown.
        - No explanations.
        - Follow the selected CSS framework rules below.
        - Use ONLY the provided design tokens.
        - Do not invent new colors.
        
        CSS Framework Selected:
        {css_framework}
        
        CSS Rules:
        {css_rules}
        
        Design Tokens:
        {design_tokens}
        """

    reply = llm.invoke([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ])

    return {
        "generated_code": reply.content,
        "validation_errors": None,
        "is_valid": None
    }

def validate_component_llm(state: GraphState):
    print("Validating Component")

    code = state["generated_code"]
    user_prompt = state["user_prompt"]
    css_framework = state["css_framework"]

    validator_llm = llm.with_structured_output(ValidationResult)

    system_prompt = f"""
        You are a strict Angular code validator.
        
        Validate the component according to:
        
        1. It must satisfy the user's request.
        2. It must strictly follow the selected CSS framework.
        3. It must use ONLY the provided design tokens.
        4. Angular syntax must appear valid.
        5. No unauthorized colors or styling systems allowed.
        
        Selected CSS Framework:
        {css_framework}
        
        Design Tokens:
        {design_tokens}
        
        Return structured validation result.
        """

    result = validator_llm.invoke([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"""
            User Prompt:
            {user_prompt}
            
            Generated Component:
            {code}
            """}
        ])

    return {
        "validation_errors": result.errors,
        "is_valid": result.valid
    }


def fix_component(state: GraphState):
    print("Fixing Component")

    errors = state["validation_errors"]
    code = state["generated_code"]
    css_framework = state["css_framework"]

    system_prompt = f"""
        You are an expert Angular engineer.
        
        The previous component failed validation.
        
        Errors:
        {errors}
        
        Original Code:
        {code}
        
        You must:
        - Fix ALL issues.
        - Strictly follow the selected CSS framework.
        - Use only the design tokens.
        - Return raw Angular code only.
        - No markdown. No explanation.
        
        Selected CSS Framework:
        {css_framework}
        
        Design Tokens:
        {design_tokens}
        """

    reply = llm.invoke([
        {"role": "system", "content": system_prompt}
    ])

    return {
        "generated_code": reply.content,
        "retry_count": state["retry_count"] + 1
    }

def modify_component(state: GraphState):
    print("Modifying Component")

    previous_code = state["previous_code"]
    user_prompt = state["user_prompt"]
    css_framework = state["css_framework"]

    system_prompt = f"""
        You are a senior Angular engineer.
        
        You will MODIFY an existing Angular standalone component.
        
        STRICT RULES:
        - Preserve existing structure unless modification requires change.
        - Do NOT regenerate from scratch.
        - Apply only the requested modification.
        - Follow selected CSS framework.
        - Use only provided design tokens.
        - Return raw Angular code only.
        - No markdown. No explanation.
        
        Selected CSS Framework:
        {css_framework}
        
        Design Tokens:
        {design_tokens}
        """

    user_message = f"""
        Previous Component:
        {previous_code}
        
        Modification Request:
        {user_prompt}
        """

    reply = llm.invoke([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message}
    ])

    return {
        "generated_code": reply.content,
        "validation_errors": None,
        "is_valid": None
    }

def route_generation(state: GraphState) -> str:
    if state.get("previous_code"):
        return "modify"
    return "generate"

def should_retry(state: GraphState) -> str:
    if not state["is_valid"] and state["retry_count"] < state["max_retries"]:
        return "fix"
    return "end"

def finalize(state: GraphState):
    return {
        "final_code": state["generated_code"]
    }