from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.routes import router

app = FastAPI(title="MietShield API", description="Backend for German Tenant Law Assistant")

# PRODUCTION NOTE:
# In a real production environment, allow_origins should NOT be ["*"].
# It should be strictly limited to the actual domain of the frontend (e.g., ["https://mietshield.com"]).
# Wildcards are used here only for local development ease.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")

@app.get("/health")
async def health_check():
    """Simple health check endpoint for monitoring uptime."""
    return {"status": "OK"}

# ---------------------------------------------------------
# HOW TO RUN IN DEVELOPMENT:
# uvicorn backend.main:app --reload
# .\.venv\Scripts\uvicorn.exe backend.main:app --reload
# ---------------------------------------------------------
