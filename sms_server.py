import os
import uvicorn
from fastapi import FastAPI, Request, BackgroundTasks
import africastalking
from agent import get_agent_client, create_chat_session
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Matatu Sasa SMS Webhook")

# Initialize Africa's Talking
AT_USERNAME = os.getenv("AT_USERNAME", "sandbox")
AT_API_KEY = os.getenv("AT_API_KEY", "")

if AT_API_KEY:
    africastalking.initialize(AT_USERNAME, AT_API_KEY)
    sms = africastalking.SMS
else:
    sms = None
    print("Warning: AT_API_KEY not set. SMS sending will be simulated in terminal.")

# Initialize Gemini Client
try:
    gemini_client = get_agent_client()
except Exception as e:
    gemini_client = None
    print(f"Warning: Could not initialize Gemini client: {e}")

# In-memory store for chat sessions: { "phoneNumber": chat_session }
chat_sessions = {}

def process_and_reply(phone_number: str, text: str):
    print(f"\n[INCOMING] from {phone_number}: {text}")
    
    if not gemini_client:
        reply_text = "Pole, Matatu Sasa AI is currently offline. Please set GEMINI_API_KEY."
        send_sms(phone_number, reply_text)
        return
        
    # Get or create chat session
    if phone_number not in chat_sessions:
        print(f"[*] Creating new chat session for {phone_number}")
        chat_sessions[phone_number] = create_chat_session(gemini_client)
        
    session = chat_sessions[phone_number]
    
    try:
        response = session.send_message(text)
        reply_text = response.text
    except Exception as e:
        reply_text = "Pole, I ran into an error finding that route. Please try again later."
        print(f"Error calling Gemini: {e}")
        
    # Send response via AT
    send_sms(phone_number, reply_text)

def send_sms(phone_number: str, text: str):
    print(f"[OUTGOING] to {phone_number}: {text}")
    
    # Optional: Shorten very long messages if needed since SMS is 160 chars.
    # Usually AT handles multipart SMS automatically, so we'll just send it.
    
    if sms:
        try:
            # AT expects recipients as a list
            response = sms.send(text, [phone_number])
            print(f"[AT SDK Response]: {response}")
        except Exception as e:
            print(f"Error sending SMS via AT: {e}")
    else:
        print("[SIMULATED SMS] No AT_API_KEY provided in .env, skipping real SMS send.")

@app.post("/incoming-messages")
async def incoming_messages(request: Request, background_tasks: BackgroundTasks):
    """
    Africa's Talking hits this endpoint with POST form data.
    """
    form_data = await request.form()
    
    # Extract fields (AT usually sends 'phoneNumber', but we check 'from' just in case)
    phone_number = form_data.get("phoneNumber", form_data.get("from", ""))
    text = form_data.get("text", "").strip()
    
    if not phone_number or not text:
        return {"status": "error", "message": "Missing phoneNumber or text payload"}
        
    # Process the message in the background to respond to AT webhook instantly (preventing timeouts)
    background_tasks.add_task(process_and_reply, phone_number, text)
    
    # Africa's Talking requires a 200 OK or it will retry
    return {"status": "success"}

if __name__ == "__main__":
    uvicorn.run("sms_server:app", host="0.0.0.0", port=8000, reload=True)
