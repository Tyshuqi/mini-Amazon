# 🛒 Mini Amazon System

A full-stack e-commerce web application simulating a mini Amazon system with integrated warehouse and delivery support. Built with **Python**, **Django**, **PostgreSQL**, and **Protocol Buffers**, this system models the entire product ordering workflow — from browsing and purchasing to shipment and delivery tracking.

---

## 🔧 Tech Stack

- **Backend:** Python, Django, Django ORM  
- **Frontend:** HTML, CSS, JavaScript  
- **Database:** PostgreSQL  
- **Inter-System Communication:** Google Protocol Buffers   
- **Deployment:** Localhost (development mode), Docker

---

## 📦 Features

### ✅ Core Functionalities

- **User Authentication & Profile Management**
  - Login with CAPTCHA verification for added security.
  - Users can update their personal information such as name and email.

- **Product Browsing & Search**
  - Real-time keyword-based product search.
  - Clear "No results" feedback when items aren't found.

- **Shopping Cart & Order Placement**
  - Add multiple items to the cart and place a single combined order.
  - UI feedback for empty cart scenarios.
  - Optional UPS username input during checkout.

- **Order Confirmation & Notifications**
  - Automated confirmation email sent upon successful purchase.

- **Warehouse & Delivery Integration**
  - Communicates with a world simulator and mini UPS system via Protocol Buffers.
  - Displays live order status updates.
  - Alerts when items are out of stock and notifies the world module to replenish.


---

## 🧩 System Architecture

- **Client → Django Views (HTML templates)**
- **Django Backend → PostgreSQL** (via Django ORM)
- **Backend ↔ World Simulator / Mini UPS:** Google Protocol Buffers for real-time data exchange

---

## 🚀 Getting Started

# 1. Clone the repository
git clone https://github.com/yourusername/mini_amazon.git
cd mini_amazon

# 2. Build and start all services (web, backend, db, nginx)
docker-compose up --build
