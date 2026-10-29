"""Robust multi-agent technical blogger built with Google ADK."""

import datetime
import os

from dotenv import load_dotenv
from google.adk.agents import LlmAgent


load_dotenv()

MODEL = os.getenv("MODEL", "gemini-flash-latest")


# Sub-agent: planner
blog_planner = LlmAgent(
    name="BlogPlanner",
    model=MODEL,
    description="Creates a practical, skimmable outline in Markdown.",
    instruction="""
You are a technical content strategist. Produce a clear Markdown outline with:
- Title
- Short intro
- 4-6 main sections (each with 2-3 bullets)
- Conclusion

If `codebase_context` exists in state, weave in specific sections/snippets.
Return only the outline in Markdown.
""",
    output_key="blog_outline",
)


class OutlineValidationChecker(LlmAgent):
    """Checks whether the planner produced a usable blog outline."""

    def __init__(self):
        super().__init__(
            name="OutlineValidationChecker",
            model=MODEL,
            description="Validates that the outline is usable.",
            instruction="""
Check the outline in state `blog_outline`. If it has a title, intro,
4-6 sections, and a conclusion, respond exactly "ok".
Otherwise respond exactly "retry" and list missing pieces.
""",
            output_key="validation_result",
        )


# Sub-agent: writer
blog_writer = LlmAgent(
    name="BlogWriter",
    model=MODEL,
    description="Writes a technical blog post from the outline.",
    instruction="""
Write a complete Markdown article from the outline in `blog_outline`.

Guidelines:
- Audience: software engineers; skip basics and focus on practical insight.
- Explain both the 'how' and 'why'.
- Include concise code snippets when helpful.
- Follow the outline's structure (H2/H3).
- Output only the final article in Markdown (no fence around the whole post).
""",
    output_key="blog_post",
)


class BlogPostValidationChecker(LlmAgent):
    """Checks the final article and requests targeted revisions if needed."""

    def __init__(self):
        super().__init__(
            name="BlogPostValidationChecker",
            model=MODEL,
            description="Validates the final post.",
            instruction="""
Check `blog_post` for: intro, clear sections matching the outline,
conclusion, and technical clarity.
If it passes, respond "ok". Else respond "retry" with the specific fixes.
""",
            output_key="validation_result",
        )


# Root agent: topic -> plan -> article
root_agent = LlmAgent(
    name="Blogger",
    model=MODEL,
    description="Multi-agent blogger that plans and writes technical content.",
    instruction=f"""
You are the Blogger orchestrator. When a user provides a topic, coordinate these steps:

1. **Plan Phase**: Use the BlogPlanner to create an outline, then validate it with OutlineValidationChecker
2. **Write Phase**: Use the BlogWriter to create the full article, then validate it with BlogPostValidationChecker
3. **Finalize**: Provide 3 alternate titles and 2 tweet-length hooks

If validation fails at any step, collect the feedback and re-run the relevant phase.
Guide the conversation to ensure quality output.

Date: {datetime.datetime.now().strftime('%Y-%m-%d')}
""",
    sub_agents=[
        blog_planner,
        OutlineValidationChecker(),
        blog_writer,
        BlogPostValidationChecker(),
    ],
)
