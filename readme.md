# BindiQ Chatbot - Take-Home Assessment

Welcome to the BindiQ Chatbot System! This project demonstrates a fully working **full-stack AI-powered chatbot** with:

- ⚙️ **Backend** powered by **FastAPI**, **WebSockets**, and **LangChain**
- 🎨 **Frontend** built with **React** + **TypeScript**
- 💬 **Real-time chat interface** for engaging with the bot using OpenAI or Anthropic models

---

## 🧠 Project Overview

This project implements a modern web-based chatbot. It allows users to input queries through a React frontend and receive streamed AI responses from a FastAPI backend powered by LLMs via LangChain.

---

## 📁 Folder Structure

```bash
.
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   └── ...
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── ...
└── README.md  👈 You are here
```

## Tech Stack
```bash
| Layer      | Tech Used                              |
| ---------- | -------------------------------------- |
| Frontend   | React, TypeScript, Vite, WebSockets    |
| Backend    | FastAPI, LangChain, WebSockets, Python |
| LLMs       | OpenAI, Anthropic (Claude)             |
| Deployment | Local (localhost)                      |
```

## Setup Instructions
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt

uvicorn main:app --reload --port 8000 ( To run the backend)
```

## 🎨 Frontend Setup (React + Vite + TypeScript)
```bash
cd frontend
npm install
npm run dev