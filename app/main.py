from fastapi import FastAPI
from app.engine.graph import build_graph
from app.api.schemas import GenerateRequest, GenerateResponse
from app.api.session_store import session_store
from fastapi.responses import StreamingResponse
from io import BytesIO

app = FastAPI(title="Guided Component Architect API")

graph = build_graph()

@app.post("/generate", response_model=GenerateResponse)
def generate_component(request: GenerateRequest):

    previous_code = session_store.get_previous_code(request.session_id)

    initial_state = {
        "user_prompt": request.prompt,
        "css_framework": request.css_framework.lower(),
        "previous_code": previous_code,
        "generated_code": None,
        "validation_errors": None,
        "is_valid": None,
        "retry_count": 0,
        "max_retries": 2,
        "final_code": None
    }

    final_state = graph.invoke(initial_state)

    session_store.save_code(
        request.session_id,
        final_state["final_code"]
    )

    return GenerateResponse(
        session_id=request.session_id,
        code=final_state["final_code"],
        retries=final_state["retry_count"]
    )


@app.post("/reset/{session_id}")
def reset_session(session_id: str):
    session_store.reset(session_id)
    return {"message": "Session reset successfully"}

@app.get("/export/{session_id}")
def export_component(session_id: str):

    code = session_store.get_previous_code(session_id)
    if not code:
        return {"error": "No component found for this session"}

    filename = "generated.component.ts"

    return StreamingResponse(
        BytesIO(code.encode("utf-8")),
        media_type="text/typescript",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )