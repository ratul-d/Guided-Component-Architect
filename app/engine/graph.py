from langgraph.graph import StateGraph, START, END
from app.engine.state import GraphState
from app.engine.nodes import (
    generate_component,
    modify_component,
    validate_component_llm,
    fix_component,
    should_retry,
    finalize,
    route_generation
)

def build_graph():
    graph_builder = StateGraph(GraphState)

    graph_builder.add_node("generate", generate_component)
    graph_builder.add_node("modify", modify_component)
    graph_builder.add_node("validate", validate_component_llm)
    graph_builder.add_node("fix", fix_component)
    graph_builder.add_node("finalize", finalize)

    graph_builder.add_conditional_edges(
        START,
        route_generation,
        {
            "generate": "generate",
            "modify": "modify"
        }
    )

    graph_builder.add_edge("generate", "validate")
    graph_builder.add_edge("modify", "validate")

    graph_builder.add_conditional_edges(
        "validate",
        should_retry,
        {
            "fix": "fix",
            "end": "finalize"
        }
    )

    graph_builder.add_edge("fix", "validate")
    graph_builder.add_edge("finalize", END)

    return graph_builder.compile()
