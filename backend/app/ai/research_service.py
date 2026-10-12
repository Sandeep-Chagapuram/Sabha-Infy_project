import httpx
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from app.core.config import settings
from app.schemas.intelligence import ResearchBriefResponse, ResearchSource
from app.ai.provider import qualcomm_client, QualcommAuthMissingError
from app.ai.model_router import QualcommModelRouter

class ResearchService:
    """
    Research Assistant workflow:
    1. Extracts or receives research questions from meeting.
    2. Retrieves genuine external web sources via search API (Tavily or DuckDuckGo API).
    3. Synthesizes findings strictly using Qualcomm Cloud AI Playground.
    Never fabricates URLs, citations, or statistics.
    """

    @classmethod
    async def fetch_web_sources(cls, query: str, max_results: int = 3) -> List[ResearchSource]:
        """Fetches verifiable external web sources."""
        sources: List[ResearchSource] = []
        now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

        # 1. Check Tavily if configured
        if settings.TAVILY_API_KEY:
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    resp = await client.post(
                        "https://api.tavily.com/search",
                        json={
                            "api_key": settings.TAVILY_API_KEY,
                            "query": query,
                            "search_depth": "basic",
                            "include_raw_content": False,
                            "max_results": max_results
                        }
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        for r in data.get("results", []):
                            sources.append(
                                ResearchSource(
                                    title=r.get("title", "Untitled Source"),
                                    url=r.get("url", ""),
                                    publication_date=r.get("published_date"),
                                    retrieval_date=now_str,
                                    excerpt=r.get("content", "")[:350]
                                )
                            )
                        return sources
            except Exception:
                pass  # Fall through to public search

        # 2. Public DuckDuckGo Instant Answer API fallback (Verifiable, no auth required)
        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                resp = await client.get(
                    "https://api.duckduckgo.com/",
                    params={"q": query, "format": "json", "no_redirect": 1, "no_html": 1}
                )
                if resp.status_code == 200:
                    data = resp.json()
                    abstract = data.get("AbstractText")
                    source_url = data.get("AbstractURL")
                    source_name = data.get("AbstractSource") or "Public Encyclopedia / Reference"
                    if abstract and source_url:
                        sources.append(
                            ResearchSource(
                                title=source_name,
                                url=source_url,
                                publication_date=None,
                                retrieval_date=now_str,
                                excerpt=abstract[:350]
                            )
                        )
                    # Check RelatedTopics
                    for topic in data.get("RelatedTopics", [])[:max_results - len(sources)]:
                        if isinstance(topic, dict) and topic.get("FirstURL") and topic.get("Text"):
                            sources.append(
                                ResearchSource(
                                    title=topic.get("Text", "").split(" - ")[0][:60],
                                    url=topic.get("FirstURL"),
                                    publication_date=None,
                                    retrieval_date=now_str,
                                    excerpt=topic.get("Text")[:300]
                                )
                            )
        except Exception:
            pass

        return sources

    @classmethod
    async def generate_research_brief(
        cls,
        question: str,
        context: Optional[str] = None
    ) -> ResearchBriefResponse:
        now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        sources = await cls.fetch_web_sources(question)

        # Check if Qualcomm Cloud AI Playground is configured
        if not qualcomm_client.is_configured():
            # Honest reporting: explain what is missing without fabricating
            if sources:
                summary = f"External search retrieved {len(sources)} source(s), but Qualcomm Cloud AI LLM synthesis is offline because QUALCOMM_API_KEY is not set."
            else:
                summary = "Research assistant requires live web access and QUALCOMM_API_KEY for synthesis. Neither external sources nor Qualcomm LLM inference was available."

            return ResearchBriefResponse(
                question=question,
                summary=summary,
                key_findings=[s.excerpt[:150] for s in sources] if sources else ["No external verified findings available."],
                sources=sources,
                uncertainty_and_limitations="Model synthesis unverified due to missing Qualcomm Cloud AI credentials.",
                suggested_follow_ups=["Configure QUALCOMM_API_KEY in .env to enable deep synthesis across search results."],
                model_name="unconfigured"
            )

        # Route LLM synthesis strictly to Qualcomm Cloud AI
        routing = QualcommModelRouter.route_task(task_category="research_synthesis")
        selected_model = routing.selected_model

        source_text_block = "\n\n".join([
            f"Source [{i+1}] ({s.title} - {s.url}):\n{s.excerpt}"
            for i, s in enumerate(sources)
        ]) if sources else "No external web sources were retrieved. Base your response only on verified knowledge and explicitly flag uncertainties."

        prompt = f"""You are the Sabha AI Research Assistant powered exclusively by Qualcomm Cloud AI.
Synthesize a concise, fact-checked research brief for this meeting question:
"{question}"

Project Context: {context or "General team collaboration"}

Retrieved Evidence Sources:
{source_text_block}

Respond ONLY with a valid JSON object matching this schema:
{{
  "summary": "1-2 sentence executive answer grounded in the sources",
  "key_findings": ["Key finding 1 with source reference", "Key finding 2"],
  "uncertainty_and_limitations": "Explicitly identify conflicts, missing data, or unverified claims",
  "suggested_follow_ups": ["Next action item or verification step for the team"]
}}"""

        result = await qualcomm_client.chat_completion(
            messages=[
                {"role": "system", "content": "You are a research synthesis agent. Respond strictly with valid JSON."},
                {"role": "user", "content": prompt}
            ],
            model=selected_model,
            temperature=0.2,
            max_tokens=1024
        )

        try:
            # Parse JSON
            raw_content = result.content.strip()
            # Clean markdown code block wraps if present
            if raw_content.startswith("```"):
                raw_content = raw_content.split("```")[1]
                if raw_content.startswith("json"):
                    raw_content = raw_content[4:]
                raw_content = raw_content.strip()

            parsed = json.loads(raw_content)
            return ResearchBriefResponse(
                question=question,
                summary=parsed.get("summary", "Synthesis completed."),
                key_findings=parsed.get("key_findings", []),
                sources=sources,
                uncertainty_and_limitations=parsed.get("uncertainty_and_limitations", "None noted."),
                suggested_follow_ups=parsed.get("suggested_follow_ups", []),
                model_name=result.model
            )
        except Exception:
            return ResearchBriefResponse(
                question=question,
                summary=result.content[:300],
                key_findings=["Direct synthesis output: " + result.content[:200]],
                sources=sources,
                uncertainty_and_limitations="Output was delivered in raw text format.",
                suggested_follow_ups=["Review full text output."],
                model_name=result.model
            )
