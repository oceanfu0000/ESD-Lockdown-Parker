# 🔐 ESD Lockdown ~~Houser~~ Parker 🚀
ESD Lockdown Parker is a **microservices-based system** designed for event-driven communication using 📨 RabbitMQ and Composite Microservices. It manages critical functionalities such as **access control, event logging, error handling, payments,** and **notifications** within a distributed architecture, ensuring seamless communication between services. (Thanks ChatGPT! 🤖)

## 🛠️ 1. Prerequisites

Make sure you have the following on your computer
- Docker 🐳
- Visual Studio Code 💻

and many more... (TBC)

## 🚀 2. Set Up
⚠️ ***Make sure you have the .env file in the project folder!***

📂 Navigate to the root directory of the project (ESD-Lockdown-Parker) and run:
```
docker compose up --build -d
```
🔄 Please remember to include build as we might be changing the code as needed.

🖥️ To run frontend, do:
```
python3 -m http.server 8100
```
📌 For list of ports, check **Notes.md**

❌ When you’re done, remember to shut everything down:
```
docker compose down
```

## ❓ 3. FAQs
❓ **Q: Why isn't Port xxx working / My endpoint isn't responding 🥲**

💡 A: Port number might be different from the initial Postman sent to the group! Please go to the file and change your port number in the API call accordingly :D

❓ **Q: Email Service is not working!**

💡 A: Firstly, check if you are missing a credentials.json file! If you are, please go to the telegram chat and add it in.

Next, Your token has expired/doesn't exist! Please do the following:
```
docker compose down
python3 -m venv .venv
source .venv/bin/activate
pip3 install -r requirements.txt
cd emailservice
python3 emailservice.py
```
Afterwards, go to postman and run http://127.0.0.1:8088/email (POST)

When prompted to login, please log in with the following details

**Email:** serviceatpark@gmail.com

**Password:** lockdownparkerservice

Token should be generated! Now you can docker compose up again :)

❓ Q: If I paint my laptop screen black, will it save battery life?

🔥 A: Absolutely! And if you paint it white again, you’ll have a built-in dark mode toggle.


