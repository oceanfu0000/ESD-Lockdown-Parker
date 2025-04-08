
# 🔐 **ESD Lockdown ~~Houser~~ Parker** 🚀

**ESD Lockdown Parker** is a **microservices-based system** designed for event-driven communication using 📨 **RabbitMQ** and **Composite Microservices**. It manages critical functionalities such as **access control**, **event logging**, **error handling**, **payments**, and **notifications** within a distributed architecture, ensuring seamless communication between services. *(Thanks, ChatGPT! 🤖)*


## 🛠️ **1. Prerequisites**

Before starting, make sure you have the following installed on your computer:

- Docker 🐳
- Visual Studio Code 💻


## 🚀 **2. Set Up**

### ⚠️ **Important:**
Make sure you have the `.env` **(root)**, `esdlocking.json` **(telegramservice)** , `credentials.json` and `token.json` **(emailservice)** file in your project folder!

**Missing token.json?**

Your token has expired/doesn't exist! Please do the following:
```
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

Token should be generated! You may proceed to step 1

### 🔧 **Step-by-Step Instructions:**


1. **Navigate to the root directory of the project**:
   ```
   cd ESD-Lockdown-Parker
   ```

2. **Run Docker Compose** to start the services:
   ```
   docker compose up --build -d
   ```
   > **Note**: Always include `--build` if you're making code changes to rebuild the containers.

## 🖥️ **3. Running the Frontend**

To access the frontend, go to http://localhost:8100/home.html


## 📌 **4. Important Information**

For the list of ports, check out **Notes.md** for details about the different services running and their corresponding ports.

To view API documentation for the respective services, go to http://localhost:[port number]/apidocs

If there is no endpoint for the files (API), you can use pydocs to read the documentation. E.g.

```
python -m pydoc amqp_setup
```


## ❌ **5. Shutting Down**

Once you're done with testing, don't forget to shut down everything:
```
docker compose down
```
---

Feel free to reach out if you encounter any other issues! 😊
