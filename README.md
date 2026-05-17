# Matatu Sasa 🚐 

**Matatu Sasa** is a street-smart, helpful, and friendly Nairobian route intelligence agent built for **Agentathon 2026 (Track 01)**. It helps people navigate the informal matatu transit system in Nairobi using localized language (English, Sheng, and Swahili). 

It intelligently handles messy transit information, reasons through multi-leg journeys, considers time-of-day traffic, and handles uncertainty natively. The agent is accessible via Web Chat, SMS, and USSD.

## ✨ Features
- **Nairobian Persona**: Speaks Sheng and Swahili natively.
- **Smart Routing**: Multi-leg route calculation and fare estimation.
- **Context-Aware Tools**: Uses live time checks and mock traffic updates to adjust fare predictions (e.g., peak hour hikes).
- **Omnichannel**: 
  - 🖥️ **Web UI**: Built with Streamlit for a great desktop/mobile web experience.
  - 📱 **SMS**: Full WhatsApp/SMS chat capability via Africa's Talking.
  - 📞 **USSD**: Fast, concise synchronous routing via Africa's Talking USSD.

## 🛠️ Technology Stack
- **AI Model**: Google Gemini 2.5 Flash (via `google-genai` Native Tool Calling)
- **Web UI**: Streamlit
- **Backend / Webhooks**: FastAPI & Uvicorn
- **Telecom API**: Africa's Talking Python SDK

---

## 🚀 Getting Started

### 1. Prerequisites
Ensure you have Python 3.10+ installed. Install the required dependencies:
```bash
pip install -r requirements.txt
```

### 2. Environment Variables
Create a `.env` file in the root directory and add your API keys:
```env
GEMINI_API_KEY=your_gemini_api_key_here
AT_USERNAME=sandbox
AT_API_KEY=your_africas_talking_sandbox_key
```

---

## 🖥️ Running the Web App (Streamlit)
To launch the beautiful chat interface locally:
```bash
streamlit run app.py
```
This will open the application in your default web browser at `http://localhost:8501`.

---

## 📱 Running the SMS & USSD Server (Africa's Talking)
To allow the agent to receive text messages and USSD sessions, run the FastAPI backend server:

1. Start the server:
```bash
python sms_server.py
```
*(The server runs on port 8000).*

2. Expose the port to the internet using `ngrok`:
```bash
ngrok http 8000
```

3. **Configure Africa's Talking Sandbox**:
   - For **SMS**: Go to *SMS > SMS Callback URLs > Incoming Messages* and paste:  
     `https://<your-ngrok-url>/incoming-messages`
   - For **USSD**: Go to *USSD > Create Channel* and set the callback URL to:  
     `https://<your-ngrok-url>/ussd`

4. Open the [Africa's Talking Simulator](https://simulator.africastalking.com:1517/) and start chatting with the agent!

---

## 🧪 Testing Locally
If you want to test the USSD flow without ngrok or Africa's Talking, simply run the test script while the `sms_server.py` is running:
```bash
python test_ussd.py
```
