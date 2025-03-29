# 🏗️ Architectural Designs for CP3407's "MyClean" Solution

This document outlines the high-level architectural design of the *MyClean* platform.

The system follows a **modular, layered architecture** with a focus on scalability, maintainability, and clear separation of concerns.

---

## 📐 Tool Used
We used [draw.io](https://app.diagrams.net/) to sketch architectural concepts and system structure.

---

## 🧱 System Architecture Overview

The MyClean application consists of:

- **Frontend (Client Web App)**  
  Built with HTML/CSS and JavaScript (templating via Flask). Provides interfaces for customers and cleaners to interact with the system.

- **Backend (API Server)**  
  A Python Flask-based REST API that handles business logic, booking workflows, user sessions, and data communication with the database.

- **Databases**  
  - **Local: SQLite (Testing)**  
  - **Production: PostgreSQL**  
  Stores persistent data such as user profiles, cleaner availability, bookings, custom checklists, and feedback.

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
- Established initial backend + database structure
- Enabled booking creation and user profile logic
- Focused on functional core features

### 🌀 Iteration 2
- Added feedback, reliability scores, and checklist integration
- Designed cleaner-specific views and customer management tools
- Deprioritized extended features (availability map, recurring jobs)

---

## ✅ Summary

This modular and scalable architecture allows *MyClean* to evolve with future features such as real-time tracking, push notifications, or microservices without requiring a full rewrite.
