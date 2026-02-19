from app.engine.graph import build_graph
from rich.console import Console
from rich.panel import Panel

console = Console()
graph = build_graph()

previous_code = None  # Memory

def run():
    global previous_code

    print("\n===== Guided Component Architect =====\n")

    css_choice = input("Choose CSS framework (tailwind/angular-material/custom): ").lower()

    while True:
        user_input = input("\nDescribe component (or 'exit'): ")

        if user_input.lower() == "exit":
            print("Goodbye")
            break

        initial_state = {
            "user_prompt": user_input,
            "css_framework": css_choice,
            "previous_code": previous_code,
            "generated_code": None,
            "validation_errors": None,
            "is_valid": None,
            "retry_count": 0,
            "max_retries": 2,
            "final_code": None
        }

        final_state = graph.invoke(initial_state)

        previous_code = final_state["final_code"]

        console.print(Panel(
            final_state["final_code"],
            title="Angular Component"
        ))

if __name__ == "__main__":
    run()
