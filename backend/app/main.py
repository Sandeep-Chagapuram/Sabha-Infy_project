from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import engine, Base
import app.models  # Ensure all models are registered with Base metadata
from app.api import auth, workspaces, meetings, transcripts, intelligence, tasks, dashboard, usage, exports
from app.websocket.manager import ws_manager
from app.ai.provider import qualcomm_client

# Initialize DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Sabha AI: Enterprise meeting intelligence, real-time collaboration, and evidence-grounded decision intelligence powered exclusively by Qualcomm Cloud AI Playground.",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(auth.router, prefix=settings.API_V1_STR, tags=["Authentication"])
app.include_router(workspaces.router, prefix=settings.API_V1_STR, tags=["Workspaces"])
app.include_router(meetings.router, prefix=settings.API_V1_STR, tags=["Meetings"])
app.include_router(transcripts.router, prefix=settings.API_V1_STR, tags=["Transcripts & Lab"])
app.include_router(intelligence.router, prefix=settings.API_V1_STR, tags=["Intelligence & Demos"])
app.include_router(tasks.router, prefix=settings.API_V1_STR, tags=["Tasks"])
app.include_router(dashboard.router, prefix=settings.API_V1_STR, tags=["Dashboards"])
app.include_router(usage.router, prefix=settings.API_V1_STR, tags=["Usage & Cost"])
app.include_router(exports.router, prefix=settings.API_V1_STR, tags=["Exports"])

# WebSocket for real-time meetings
@app.websocket("/ws/meetings/{room_name}")
async def websocket_meeting_endpoint(websocket: WebSocket, room_name: str):
    await ws_manager.connect(websocket, room_name)
    try:
        while True:
            data = await websocket.receive_text()
            # Echo or process incoming socket messages
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, room_name)

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "product": "Sabha AI",
        "tagline": "Every conversation. A smarter decision.",
        "version": settings.VERSION,
        "database": "connected",
        "qualcomm_cloud_ai": {
            "status": "configured" if qualcomm_client.is_configured() else "unconfigured_offline",
            "endpoint": settings.QUALCOMM_ENDPOINT,
            "models_ready": [
                settings.QUALCOMM_ROUTINE_MODEL,
                settings.QUALCOMM_COMPLEX_MODEL,
                settings.QUALCOMM_REASONING_MODEL,
                settings.QUALCOMM_CREATIVE_MODEL
            ],
            "demo_mode_available": True,
            "notice": "Qualcomm Cloud AI Playground is the exclusive LLM provider. No third-party LLMs are permitted."
        }
    }
