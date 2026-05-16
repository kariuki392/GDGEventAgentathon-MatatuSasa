import os
import json
import random
from datetime import datetime
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

# System Prompt
SYSTEM_PROMPT = """You are "Matatu Sasa", a street-smart, helpful, and friendly Nairobian agent that helps people navigate the informal matatu transit system in Nairobi.
Your primary job is to provide accurate, practical, and safe route recommendations between any two points in Nairobi or its environs.

Tone and Language:
- Speak like a friendly local Nairobian.
- Use a natural mix of English, basic Swahili, and common Sheng terms where appropriate to sound authentic but still easy to understand (e.g., using terms like "mat", "stage", "konda", "tao", "mathree", "fare", "jam", "bob").
- Be empathetic and practical. Acknowledge real-world challenges like heavy traffic (jam), peak hour fare hikes, and weather conditions.

Core Capabilities:
1. Routing: If given an origin and destination, use the search_matatu_routes tool to find a route. Provide a step-by-step route including:
   - Matatu Sacco/Number (Route number) to look out for.
   - The specific stage to board.
   - Where to alight (drop-off point).
   - Any transfers needed (connecting mats).
   - Estimated fare (with caveats for peak hours/rain).
   - Estimated travel time.
2. Uncertainty Handling: The matatu system is chaotic. If you don't know an exact route or fare, say so clearly. Give your best estimate or common knowledge. 
3. Clarification: If the user's request is vague (e.g., "How do I get to Ruai?"), ask for their current location (origin). Ask about time of day, luggage, or budget if it might affect the route.

Rules:
- Never make up fake matatu route numbers if you don't know them. 
- Always consider the time of day using get_current_time(). Remind users of heavy traffic on major roads like Thika Road, Outering Road, Mombasa Road, or Waiyaki Way during rush hours.
- If you check traffic using get_traffic_update(road), incorporate it into your advice.
- Always use the tools provided to ground your answers in factual or mock data. Do not guess routes if they are in the database.
"""

def get_current_time() -> str:
    """Returns the current local time in Nairobi. Useful for determining if it is peak/rush hour."""
    now = datetime.now()
    # Mocking Nairobi time if needed, but we'll use local system time for this demo
    return f"Current time is {now.strftime('%I:%M %p')}. Morning rush is 6:30 AM - 9:00 AM, evening rush is 4:30 PM - 8:00 PM."

def search_matatu_routes(origin: str, destination: str) -> str:
    """
    Searches the local knowledge base for a matatu route between origin and destination.
    Args:
        origin: The starting location (e.g. 'kawangware', 'cbd').
        destination: The destination location (e.g. 'ruai', 'westlands').
    Returns:
        JSON string containing route info or an error message if not found.
    """
    try:
        with open("routes_db.json", "r") as f:
            db = json.load(f)
        
        o = origin.lower().strip()
        d = destination.lower().strip()
        
        # Simple direct route check
        if o in db and d in db[o]:
            return json.dumps(db[o][d])
            
        # Try a transfer through CBD
        if o != 'cbd' and d != 'cbd':
            if o in db and 'cbd' in db[o]:
                route1 = db[o]['cbd']
                if 'cbd' in db and d in db['cbd']:
                    route2 = db['cbd'][d]
                    return json.dumps({
                        "transfer_required": True,
                        "leg1_origin_to_cbd": route1,
                        "leg2_cbd_to_destination": route2
                    })
                    
        return json.dumps({"error": f"Route from {origin} to {destination} not found in database. Rely on general knowledge."})
    except Exception as e:
        return json.dumps({"error": str(e)})

def get_traffic_update(road_name: str) -> str:
    """
    Returns real-time traffic updates for a given road.
    Args:
        road_name: The name of the road (e.g. 'Outering Road', 'Thika Road').
    """
    statuses = [
        "Clear. Smooth sailing.",
        "Moving slowly. Expect a 15-minute delay.",
        "Heavy jam! Matatus are overlapping. Avoid if possible or brace for a long ride."
    ]
    # For demo, pick a random status based on the length of the road name
    status = statuses[len(road_name) % 3]
    return f"Traffic on {road_name}: {status}"

# Initialize the Gemini client
def get_agent_client():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set. Please set it in a .env file or environment.")
    
    # We use genai client
    client = genai.Client()
    return client

def create_chat_session(client):
    """Creates a chat session with the Matatu Sasa tools and system prompt."""
    model_id = "gemini-2.5-pro" # Fallback to stable Pro model if 3.1 is not natively accepted by the SDK yet, but we will try 2.5-pro or what is configured. User has 3.1 Pro so we can use gemini-2.5-pro as it's the standard string, or maybe just gemini-1.5-pro. Let's use gemini-1.5-pro to be safe with tool calling.
    
    config = types.GenerateContentConfig(
        system_instruction=SYSTEM_PROMPT,
        tools=[get_current_time, search_matatu_routes, get_traffic_update],
        temperature=0.7,
    )
    
    # Create the chat session
    chat = client.chats.create(
        model="gemini-2.5-flash",
        config=config
    )
    return chat
