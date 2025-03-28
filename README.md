
# 🔐 **ESD Lockdown ~~Houser~~ Parker** 🚀

**ESD Lockdown Parker** is a **microservices-based system** designed for event-driven communication using 📨 **RabbitMQ** and **Composite Microservices**. It manages critical functionalities such as **access control**, **event logging**, **error handling**, **payments**, and **notifications** within a distributed architecture, ensuring seamless communication between services. *(Thanks, ChatGPT! 🤖)*

---

## 🛠️ **1. Prerequisites**

Before starting, make sure you have the following installed on your computer:

- Docker 🐳
- Visual Studio Code 💻

...and a few more tools to be added soon! (TBC) 

---

## 🚀 **2. Set Up**

### ⚠️ **Important:**
Make sure you have the `.env` file in your project folder!

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

---

## 🖥️ **3. Running the Frontend**

### 📱 **For macOS:**
To run the frontend, use the following command:
```
python3 -m http.server 8100 --directory ./Frontend
```

### 💻 **For Windows:**
For Windows users, run:
```
http-server ./Frontend -p 8100
```
if you run into an error, run the following:
```
npm install -g http-server
http-server ./Frontend -p 8100
```

---

## 📌 **4. Ports Information**

For the list of ports, check out **Notes.md** for details about the different services running and their corresponding ports.

---

## ❌ **5. Shutting Down**

Once you're done with testing, don't forget to shut down everything:
```
docker compose down
```

---

## ❓ **6. FAQs**

### **❓ Q: Why isn't Port xxx working / My endpoint isn't responding 🥲**
💡 **A:** The port number might differ from the one initially shared in the Postman collection! Please check the file and update your API calls accordingly.

---

### **❓ Q: Email Service is not working!**

💡 **A:**

1. **Missing `credentials.json`?**  
   Make sure you have the `credentials.json` file. If you don't, check the telegram chat for it.

2. **Token expired or missing?**  
   If your token has expired or doesn't exist, follow these steps:
   ```bash
   docker compose down
   python3 -m venv .venv
   source .venv/bin/activate
   pip3 install -r requirements.txt
   cd emailservice
   python3 emailservice.py
   ```

3. **Test the email service**:  
   Once the service is running, test it by sending a POST request to:
   ```
   http://127.0.0.1:8088/email
   ```
   When prompted to log in, go to the next step

4. **Login credentials for email service:**

   **Email:** serviceatpark@gmail.com  
   **Password:** lockdownparkerservice

   After successfully logging in, a token will be generated, and you can restart the services with:
   ```
   docker compose up --build -d
   ```
---

### **❓ Q: If I paint my laptop screen black, will it save battery life?**

🔥 **A:** Absolutely! And if you paint it white again, you’ll have a built-in **dark mode toggle**. 😎

---

Feel free to reach out if you encounter any other issues! 😊
