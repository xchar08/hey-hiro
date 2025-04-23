# Hey‑Hiro: Voice‐Activated AI Drone Controller

**Hey‑Hiro** is an AI assistant web app built with Next.js and Electron.  It listens for the wake phrase **“Hey Hero”** and then executes voice commands to control a swarm of Crazyflie drones (via Python scripts) or generate new flight code using the Cerebras API.  All code generation, command execution, and drone resets are routed through an Electron companion process.

---

## 🚀 Features

- **Wake‑Word Activation**: Say **“Hey Hero”** to trigger voice command mode.
- **Drone Control Commands**:
  - **Hover** specific drones (with optional duration & height).
  - **Circle** formation.
  - **V‑Formation** around a chosen leader drone.
  - **Surround** a leader drone in a ring.
  - **Spiral** pattern flight via custom demo script.
  - **Reset** individual or all drones safely.
- **AI Code Generation (Cerebras API)**:
  - For unrecognized commands, automatically generate Python drone scripts.
  - Preview generated code in UI and choose to execute via Electron.
- **Interactive UI** (Chakra UI):
  - Transcript & assistant response panels.
  - Microphone control buttons.
  - **Settings Modal**: adjust aura color, voice speed, theme, and set your Cerebras API key.
- **Electron Companion**:
  - Hosts an Express server (with CORS & body‑parser).
  - Receives command payloads from the Next.js app.
  - Executes system commands, Python scripts, and generated code.
- **Modular Drone Framework**:
  - Leverages existing `scripted_flight/` Python project with CLI parsing.
  - Supports URIs or JSON config for multi‑drone control.
  - Demo modes: `hover`, `circle`, `surround`, `v`, `spiral`.

---

## 🏗 Architecture Overview

```
+----------------------+        +-------------------+      +-----------------------+
|  Next.js Frontend    | <-->   | Electron Companion| <--> | Python Drone Scripts  |
| (React + Chakra UI)  |        | (Express server)  |      | (scripted_flight/*)   |
+----------------------+        +-------------------+      +-----------------------+
         ^   ^                          ^  ^                           ^    ^
         | Voice + HTTP                 | HTTP                       | CLI
         | Recognition                  | Command endpoints          | Drone SDK / Vicon
         v                              v                            v
   Web Speech API                  Axios calls                  Crazyflie Python lib
```

- **Frontend** listens for voice, displays transcripts & responses, and sends JSON payloads
  to the Companion server.
- **Electron Companion** receives `/droneCommand`, `/executeCode`, `/reset`, etc., executes
  Python CLI or system commands, and returns status.
- **Python Scripts** in `scripted_flight/` implement flight patterns and resets via Crazyflie SDK.

---

## 🛠 Tech Stack

- **Next.js 15** (App Router, React 18, TypeScript)
- **Chakra UI** for layout & components
- **React Icons** (`FaMicrophone`, `FaStop`, `FaCog`)
- **Web Speech API** for voice input
- **Axios** for HTTP
- **Electron** + **Express** companion process
- **Cerebras Cloud SDK** for AI completions
- **Python 3.10+** environment for drone scripts
  - Crazyflie Python library
  - Vicon DataStream SDK
  - NumPy

---

## 📋 Prerequisites

1. **Node.js & npm** (v18+)
2. **Python 3.10+**
3. **Crazyflie & Vicon** hardware & drivers installed
4. **Cerebras API Key** (set as `NEXT_PUBLIC_CEREBRAS_API_KEY`)

---

## ⚙️ Installation & Setup

### 1. Clone & Install Frontend

```bash
git clone https://github.com/your-org/hey-hiro.git
cd hey-hiro
npm install
```

### 2. Create `.env.local` in root

```dotenv
NEXT_PUBLIC_COMPANION_API_URL=http://localhost:3031
NEXT_PUBLIC_CEREBRAS_API_KEY=your_cerebras_key_here
```

### 3. Python & Companion Setup

```bash
cd companion-app
python -m venv venv
source venv/Scripts/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt     # use pyautogui, requests, bs4
```

### 4. Final Install

From repo root:
```bash
npm install express cors body-parser
npm install   # ensures companion deps are in root package.json
```

---

## ▶️ Running the App

1. **Start Next.js** (frontend):
   ```bash
   npm run dev
   ```
2. **Start Electron Companion**:
   ```bash
   npm run companion
   ```
3. Open your browser at `http://localhost:3000`.

Speak `"Hey Hero, ..."` to issue commands!

---

## 🎤 Voice Command Reference

| Command Pattern                                                             | Action                                                       |
| --------------------------------------------------------------------------- | ------------------------------------------------------------ |
| `Hey Hero, make drones 1, 2 hover`                                          | Hover drones 1 & 2 at default height & duration              |
| `Hey Hero, make drone 3 hover for 5 seconds at height 1 meter`              | Hover drone 3 for 5s at 1m                                   |
| `Hey Hero, make all drones fly in a circle`                                 | Circle formation demo                                        |
| `Hey Hero, make all drones fly in a v formation with drone 1 as leader`     | V formation demo                                             |
| `Hey Hero, make all drones surround drone 1`                                | Surround demo                                                |
| `Hey Hero, make drone 2 fly in a spiral pattern`                            | Runs custom spiral demo script                               |
| `Hey Hero, reset drone 4`                                                   | Resets individual drone                                      |
| `Hey Hero, reset all drones`                                                | Resets all drones                                            |
| **Any other command**                                                       | Generates code via Cerebras API + prompts for execution      |

---

## 🧩 File Structure

```text
hey-hiro/
├── app/                      # Next.js app
│   ├── components/
│   │   ├── SettingsModal.tsx
│   │   └── TutorialTooltip.tsx
│   ├── page.tsx              # Main client component
│   └── global.d.ts           # SpeechRecognition typings
├── companion-app/            # Electron companion server
│   ├── main.js
│   └── requirements.txt
├── scripted_flight/          # Python drone framework
│   ├── controllers/
│   ├── demos/
│   ├── config/drones.json
│   ├── main.py
│   └── reset.py
├── .env.local
├── package.json
├── tsconfig.json
└── README.md
```

---

## 🤝 Contributing

1. Fork the repo
2. Create a feature branch (`git checkout -b feature/awesome`)
3. Commit your changes
4. Open a Pull Request

---

## 📄 License

MIT © Your Name or Organization
