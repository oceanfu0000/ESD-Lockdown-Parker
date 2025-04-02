
# 🔐 **ESD Lockdown ~~Houser~~ Parker** 🚀

**ESD Lockdown Parker** is a **microservices-based system** designed for event-driven communication using 📨 **RabbitMQ** and **Composite Microservices**. It manages critical functionalities such as **access control**, **event logging**, **error handling**, **payments**, and **notifications** within a distributed architecture, ensuring seamless communication between services. *(Thanks, ChatGPT! 🤖)*


## 🛠️ **1. Prerequisites**

Before starting, make sure you have the following installed on your computer:

- Docker 🐳
- Visual Studio Code 💻



## 🚀 **2. Set Up**

### ⚠️ **Important:**
Make sure you have the `.env` **(root)**, `esdlocking.json` **(telegramservice)** , `credentials.json` and `token.json` **(emailservice)** file in your project folder!

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

   If you are having trouble running kong, run this commands
   ```
   docker-compose run --rm kong kong migrations up

   docker-compose run --rm kong kong migrations finish

   docker-compose up kong --build -d
   ```

## 🖥️ **3. Running the Frontend**

To access the frontend, go to http://localhost:8100/home.html



## 📌 **4. Important Information**

For the list of ports, check out **Notes.md** for details about the different services running and their corresponding ports.

To view API documentation for the respective services, go to http://localhost:[port number]/apidocs



## ❌ **5. Shutting Down**

Once you're done with testing, don't forget to shut down everything:
```
docker compose down
```
---

Feel free to reach out if you encounter any other issues! 😊
