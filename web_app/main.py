
import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from google.adk.runners import InMemoryRunner
from google.genai import types

from simple_blogger_agent.agent import root_agent

load_dotenv(
    Path(__file__).resolve().parent.parent
    / "simple_blogger_agent"
    / ".env"
)

app = FastAPI(title="AI Blog Generator")
runner = InMemoryRunner(agent=root_agent, app_name="blog_generator")


class BlogRequest(BaseModel):
    topic: str


@app.get("/")
async def home():
    return FileResponse(Path(__file__).parent / "index.html")


@app.post("/generate")
async def generate_blog(request: BlogRequest):
    if not request.topic.strip():
        raise HTTPException(status_code=400, detail="Enter a topic.")

    user_id = "website_user"
    session = await runner.session_service.create_session(
        app_name="blog_generator",
        user_id=user_id,
    )

    message = types.Content(
        role="user",
        parts=[
            types.Part(
                text=f"Write a blog post about {request.topic}."
            )
        ],
    )

    final_text = ""

    try:
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session.id,
            new_message=message,
        ):
            if event.is_final_response() and event.content:
                final_text = "\n".join(
                    part.text
                    for part in event.content.parts
                    if part.text
                )

        return {"blog": final_text or "No blog was generated."}

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail="The AI agent could not generate the blog.",
        ) from error
