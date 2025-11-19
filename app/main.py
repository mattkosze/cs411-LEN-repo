#quick setup using fastapi and taking in the given routers. depending on commit version not all routers may be prsent yet
from fastapi import FastAPI
from .routers import accounts, posts, moderation, crisis

app = FastAPI(
    title="LEN - Community Support Backend",
    description="Backend API for LEN patient support platform",
    version="0.1.0",
)

#including the routers here
app.include_router(accounts.router, prefix="/accounts", tags=["accounts"])
app.include_router(posts.router, prefix="/posts", tags=["posts"])
app.include_router(moderation.router, prefix="/moderation", tags=["moderation"])
app.include_router(crisis.router, prefix="/crisis", tags=["crisis"])

@app.get("/health")
def health_check():
    return {"status": "ok"}