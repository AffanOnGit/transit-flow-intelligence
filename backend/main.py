from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path
from services.transit_service import TransitService
from services.agent_service import AgentService

app = FastAPI(title="Transit Flow Intelligence API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this to your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Services
data_dir = Path(__file__).parent.parent / "data"
csv_path = data_dir / "routes.csv"

if not csv_path.exists():
    # Fallback for different directory structures
    csv_path = Path(__file__).parent / "data" / "routes.csv"

ts = TransitService(str(csv_path))
agent = AgentService(ts)

class ChatRequest(BaseModel):
    message: str

@app.get("/api/routes")
async def get_routes():
    return ts.get_available_routes()

@app.get("/api/map")
async def get_map(route_id: str = "All", threshold: float = 1.5):
    try:
        elements = ts.get_map_elements(route_id, threshold)
        return elements
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stats")
async def get_stats(route_id: str = "All", threshold: float = 1.5):
    try:
        stats = ts.get_stats(route_id, threshold)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat")
async def chat_with_agent(request: ChatRequest):
    try:
        response = agent.query(request.message)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
