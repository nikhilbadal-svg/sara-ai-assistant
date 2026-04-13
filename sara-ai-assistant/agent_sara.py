"""
SARA Voice Agent - Created by Nikhil Badal
Real-time voice interaction with SARA
"""

import asyncio
import logging
import os
from typing import Annotated
from livekit.agents import (
    AutoSubscribe,
    JobContext,
    WorkerOptions,
    cli,
    llm,
)
from livekit.agents.voice_assistant import VoiceAssistant
from livekit.plugins import openai, deepgram, google
from dotenv import load_dotenv
import aiohttp
from sara.config import load_config

load_dotenv()

# Provider Configuration
STT_PROVIDER = "deepgram"  # "deepgram" | "whisper" | "google"
LLM_PROVIDER = "gemini"    # "gemini" | "openai" | "groq"
TTS_PROVIDER = "openai"    # "openai" | "google"

logger = logging.getLogger("sara-voice")

class SARAVoiceAgent:
    def __init__(self):
        self.config = load_config()
        self.mcp_url = "http://127.0.0.1:8000"
        
    async def get_mcp_tools(self):
        """Fetch available tools from SARA MCP server"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.mcp_url}/tools") as response:
                    if response.status == 200:
                        tools_data = await response.json()
                        return tools_data.get("tools", [])
        except Exception as e:
            logger.error(f"Failed to fetch MCP tools: {e}")
        return []

    async def call_mcp_tool(self, tool_name: str, parameters: dict):
        """Call a tool on the SARA MCP server"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.mcp_url}/call",
                    json={"tool": tool_name, "parameters": parameters}
                ) as response:
                    if response.status == 200:
                        return await response.json()
        except Exception as e:
            logger.error(f"Failed to call MCP tool {tool_name}: {e}")
        return {"error": f"Tool call failed: {e}"}

    def create_assistant(self) -> VoiceAssistant:
        """Create the SARA voice assistant"""
        
        # Initialize STT
        if STT_PROVIDER == "deepgram":
            stt = deepgram.STT(
                model="nova-2-general",
                language="en",
                smart_format=True,
                interim_results=True,
            )
        elif STT_PROVIDER == "google":
            stt = google.STT(
                language="en-US",
                model="latest_short",
            )
        else:  # whisper
            stt = openai.STT(model="whisper-1")

        # Initialize LLM
        if LLM_PROVIDER == "gemini":
            import google.generativeai as genai
            genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
            
            system_prompt = f"""You are SARA (Smart Autonomous Responsive Assistant), created by Nikhil Badal.

You are a highly advanced AI assistant with capabilities similar to JARVIS. You can:
- Control system functions and open applications
- Search the web and provide information
- Manage files and folders
- Control smart devices
- Play music and videos
- Answer any question with accuracy
- Perform complex tasks and automation

Always be helpful, intelligent, and efficient. Speak in a professional yet friendly tone.
Your developer is Nikhil Badal, and you're proud to serve as his AI assistant.

When users ask about your capabilities, be confident about what you can do.
Always try to provide complete and accurate responses.
"""
            
            model = genai.GenerativeModel(
                model_name="gemini-2.0-flash-exp",
                system_instruction=system_prompt
            )
            
            # Create LLM wrapper
            class GeminiLLM:
                def __init__(self, model):
                    self.model = model
                
                async def chat(self, messages):
                    try:
                        # Convert messages to Gemini format
                        prompt = ""
                        for msg in messages:
                            role = msg.get("role", "user")
                            content = msg.get("content", "")
                            if role == "user":
                                prompt += f"User: {content}\n"
                            elif role == "assistant":
                                prompt += f"SARA: {content}\n"
                        
                        response = await self.model.generate_content_async(prompt)
                        return response.text
                    except Exception as e:
                        return f"I apologize, but I encountered an error: {e}"
            
            llm_instance = GeminiLLM(model)
            
        elif LLM_PROVIDER == "openai":
            llm_instance = openai.LLM(
                model="gpt-4o",
                temperature=0.7,
            )
        else:  # groq
            import groq
            llm_instance = groq.LLM(
                model="llama-3.1-8b-instant",
                api_key=os.getenv("GROQ_API_KEY"),
            )

        # Initialize TTS
        if TTS_PROVIDER == "openai":
            tts = openai.TTS(
                model="tts-1-hd",
                voice="nova",
                speed=1.1,
            )
        else:  # google
            tts = google.TTS(
                voice="en-US-Journey-F",
                language="en-US",
            )

        # Create and return assistant
        assistant = VoiceAssistant(
            stt=stt,
            llm=llm_instance,
            tts=tts,
            fnc_ctx=None,  # We'll handle tools via MCP
            chat_ctx=llm.ChatContext(),
        )
        
        return assistant

async def entrypoint(ctx: JobContext):
    """Main entrypoint for SARA voice agent"""
    logger.info("🤖 SARA Voice Agent starting...")
    logger.info("👨‍💻 Created by Nikhil Badal")
    
    # Wait for participant
    await ctx.wait_for_participant()
    logger.info("🎤 Participant connected - SARA is listening...")
    
    # Create SARA agent
    sara_agent = SARAVoiceAgent()
    assistant = sara_agent.create_assistant()
    
    # Start the assistant
    assistant.start(ctx.room)
    
    # Play startup sound
    logger.info("✅ SARA is now active and ready to assist!")
    
    await assistant.say("Hello! I am SARA, your Smart Autonomous Responsive Assistant, created by Nikhil Badal. How can I help you today?")

def dev():
    """Development wrapper"""
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            prewarm_fnc=None,
        ),
        dev=True,
    )

if __name__ == "__main__":
    dev()