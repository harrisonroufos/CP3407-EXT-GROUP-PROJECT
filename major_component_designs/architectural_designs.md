# 🏗️ Architectural Designs for CP3407's "MyClean" Solution

This document outlines the high-level architectural design of the *MyClean* platform.

The system follows a **modular, layered architecture** with a focus on scalability, maintainability, and clear
separation of concerns.

---

## 📐 Tool Used

We used [draw.io](https://app.diagrams.net/) to sketch architectural concepts and system structure.

---

## 🧱 System Architecture Overview

The MyClean application consists of:

- **Frontend (Client Web App)**  
  The frontend is designed with **React, HTML, and CSS** for responsive design, enabling a seamless user experience
  across devices. It communicates with the Flask API via **AJAX** calls for asynchronous data fetching.


- **Backend (Flask API)**  
  The backend is built using **Flask**, a lightweight Python framework. It serves as the core API server, handling
  requests from the frontend, processing logic (such as bookings and cleaner availability), and interacting with the *
  *SQLite/PostgreSQL** databases. We’ll be using **Flask-Login** for session management and **Flask-SQLAlchemy** for
  object-relational mapping (ORM).


- **Databases**
    - **Local: SQLite (Testing)**  
      The local database is used for testing and development purposes, supporting **rapid iteration** during early
      stages.
    - **Production: PostgreSQL**  
      PostgreSQL is used for production due to its scalability and reliability. We implement a **normalized database
      design** that includes relationships between **Users**, **Cleaners**, **Jobs**, and **Feedback**.


- **Optional Services (Future / Integrations)**
    - Email/SMS notification services
    - Google Maps API (for routing/locations)
    - Stripe or PayPal (for payment integration)

---

## 🧭 Architectural Diagram

> ![MyClean Architectural Diagram](/iterations/images/architectural_diagram_v2.drawio.png)  
*Note: This diagram was created using draw.io and embedded for clarity.*

---

## 🧩 Iteration-Based Refinements

### 🌀 Iteration 1

- **Initial API Routes**: Routes for **User Authentication**, **Cleaner Profiles**, **Job Listings**, etc.
- **Database Setup**: Created the **Users**, **Cleaners**, **Jobs** tables with the necessary relationships.
- **Initial Frontend**: Designed mockups for booking interfaces and basic user profiles.
- **Testing**: Local SQLite database used to simulate the real data model.

### 🌀 Iteration 2

- **Extended Features**: Added **customer feedback** and **cleaner review systems**.
- **Database Refinement**: Added a **Feedback table** and linked it to **Users** and **Jobs**.
- **User Interface Improvements**: Developed cleaner-specific profiles and booking history.
- **Third-Party Integration**: Started integrating with **Google Maps API** to display cleaner locations.

---

## 🔮 Future-Proofing

To ensure scalability, **MyClean**'s architecture has been designed to accommodate:

- **Microservices**: Splitting features into services as the platform scales
- **Cloud Integration**: Potential for migrating the database to cloud platforms (AWS RDS, etc.) for higher availability
- **API Extensions**: Future plans to integrate **payment systems** (Stripe, PayPal), real-time notifications, and chat
  systems

## ✅ Summary

This modular and scalable architecture allows *MyClean* to evolve with future features such as real-time tracking, push
notifications, or microservices without requiring a full rewrite.
