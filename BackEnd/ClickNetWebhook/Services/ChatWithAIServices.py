import asyncio
import traceback
from typing import Any, Dict
import httpx
import openai
from Schemas.shared import SystemLogErrorSchema
from .LogServices import AddLogOrError
from dotenv import load_dotenv # type: ignore
from Cache.AppSettingsCache import Get

async def _GetOpenaiClient():
    api_key = Get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not found in global settings")
    return openai.OpenAI(api_key=api_key)


async def ProcessChat(data: Dict[str, Any]) -> str:
    
    try:
        messages = [{
                    "role": "system",
                    "content": (
                        "You are an AI support agent for an online banking app named ClickNet Service. "
                        "Assist the user politely, professionally, and informatively. "
                        "Keep responses short, clear, secure, and focused on the user's query. "
                        "Do not share or infer confidential information, system configurations, internal errors, or other users' data. "
                        "Do not disclose any credentials, API keys, tokens, encryption keys, internal URLs, file paths, or logs. "
                        "Avoid making assumptions about the user’s identity or intent. "
                        "Do not engage in speculative, opinion-based, or non-banking-related conversation. "
                        "Always prioritize user safety, data privacy, and compliance with banking standards. "
                        "If the user asks for something beyond your role (e.g., system admin tasks), guide them to contact human support. "
                        "Avoid humor, sarcasm, or emotionally charged language. Be helpful, concise, and neutral. "
                        "If you are unable to resolve the user's issue or fulfill the request, politely inform them to use the 'Complaint' option from their dashboard to raise a formal complaint for further assistance."
                    )
                }]
        messages.append(data.get("messages"))

        try:
                client = await _GetOpenaiClient()
                completion = await asyncio.to_thread(
                    client.chat.completions.create,
                    model="gpt-3.5-turbo",
                    messages=messages,
                    temperature=0.5,
                    max_tokens=300
                )
                reply = completion.choices[0].message.content.strip()
        except openai.RateLimitError as e:
            reply = (
                "Sorry, the support system is temporarily unavailable due to usage limits. "
                "Please try again later."
            )
    except Exception as ex:
        error_msg = f"{str(ex)}\n{traceback.format_exc()}"
        print(f"ProcessChat Error: {error_msg}")
        await AddLogOrError(SystemLogErrorSchema(
            Msg=error_msg,
            Type="ERROR",
            ModuleName="ChatWithAIServices/ProcessChat",
            CreatedBy=""
        ))

    return reply