# CP3407 External Group 1

## Team Members

- Harrison Roufos
- Damon Lindsay
- Casey Summers
- Daniel Brooks
---
## To use the application
- Visit the website https://cp3407-myclean.onrender.com/
    - NOTE. This method can be slow when loading the application.

### OR

- Run app.py and visit the local ip shown in terminal.
---

## Project Requirements & User Stories (Criteria 1)

This project involved planning and documenting a large number of user stories across multiple iterations. Each story
includes:

- Polished and standardised formatting
- Prioritisation (range 1–50)
- Planning poker estimations
- Assigned iteration (1, 2, or dropped)
- UI mockups (even for dropped stories)

---

## ✅ Iteration Plans

| Iteration                                       | Duration  | Details                                                  |
|-------------------------------------------------|-----------|----------------------------------------------------------|
| [Iteration 1](./iterations/iteration_1_plan.md) | 3-4 weeks | Focus on core booking, profiles, and feedback            |
| [Iteration 2](./iterations/iteration_2_plan.md) | 3-4 weeks | Focus on reliability, checklists, cancellations, mockups |

---

## 📋 Completed User Stories

| Feature                   | Iteration | Priority | Status     | Link                                                           |
|---------------------------|-----------|----------|------------|----------------------------------------------------------------|
| Create Booking            | 1         | 10       | ✅ Complete | [View](./user_stories/user_story_create_booking.md)            |
| Booking Confirmation      | 1         | 20       | ✅ Complete | [View](./user_stories/user_story_booking_confirmation.md)      |
| Customer Feedback         | 2         | 25       | ✅ Complete | [View](./user_stories/user_story_customer_feedback.md)         |
| Reliability Scores        | 2         | 20       | ✅ Complete | [View](./user_stories/user_story_reliability_scores.md)        |
| Custom Cleaning Checklist | 1         | 40       | ✅ Complete | [View](./user_stories/user_story_custom_cleaning_checklist.md) |
| Chat With Hired Cleaner   | 2         | 25       | ✅ Complete | [View](./user_stories/user_story_chat_with_hired_cleaner.md)   |
| Browse Cleaners           | 1         | 30       | ✅ Complete | [View](./user_stories/user_story_browse_cleaners.md)           |
| Handle Cancellations      | 2         | 30       | ✅ Complete | [View](./user_stories/user_story_handle_cancellations.md)      |
| Create Cleaner Profile    | 1         | 40       | ✅ Complete | [View](./user_stories/user_story_create_cleaner_profile.md)    |

---

## ❌ Dropped / Deprioritized User Stories

| Feature                    | Iteration | Priority | Status    | Link                                                                |
|----------------------------|-----------|----------|-----------|---------------------------------------------------------------------|
| Cleaner Availability       | 2         | 20       | ❌ Dropped | [View](./user_stories/user_story_cleaner_availability.md)           |
| Recurring Job              | 2         | 50       | ❌ Dropped | [View](./user_stories/user_story_recurring_job.md)                  |
| Efficient Route Mapping    | 2         | 40       | ❌ Dropped | [View](./user_stories/user_story_efficient_route_mapping.md)        |
| Cleaning Supplies Tracking | 2         | 30       | ❌ Dropped | [View](./user_stories/user_story_cleaning_supplies_tracking.md)     |
| Referral Program           | 2         | 20       | ❌ Dropped | [View](./user_stories/user_story_referral_program_for_customers.md) |
| Create Schedule            | 2         | 30       | ❌ Dropped | [View](./user_stories/user_story_create_schedule.md)                |
| Schedule Notifications     | 2         | 40       | ❌ Dropped | [View](./user_stories/user_story_schedule_notifications.md)         |
| See Current Area Jobs      | 2         | 50       | ❌ Dropped | [View](./user_stories/user_story_see_current_area_cleaning_jobs.md) |
| Booking Reminders          | 2         | 30       | ❌ Dropped | [View](./user_stories/user_story_booking_reminders.md)              |

---

# Database Diagram

![database diagram](/database_files/myclean_database_diagram.png)

---

# UML Diagram

![uml diagram](/database_files/myclean_uml_diagram.png)

---

## 🖼️ UI Mockups

All mockups (including those for dropped features) are stored in the `/docs/ui-wireframes/` directory.  
Each mockup is linked within its respective user story, but you can also browse them all in one place.

**Examples include:**

- Cleaner Availability wireframe
- Custom Cleaning Checklist builder
- Cancel Booking interface
- Recurring Job scheduler
- Snap Map-style Nearby Cleaners view
- Referral Program screen
- Cleaning Supplies tracker
- Schedule Notifications alert view

---

## 🧪 Testing

We implemented comprehensive testing using `pytest` across all major components of the system. Our tests cover:

### ✅ Structure

- **Shared Fixtures**: All common test setup (e.g. test users, cleaners, bookings, and client) is located in
  `conftest.py` to reduce duplication and ensure consistent teardown between test runs.

- **Modular Test Files**:
    - `test_app.py`: General application behavior, login, and booking management.
    - `test_booking.py`: Booking creation, route access (GET/POST), and deletion.
    - `test_cleaner.py`: Cleaner profile view and profile editing.
    - `test_database.py`: Validates DB connection, table setup, and seed data (e.g. admin user).
    - `test_services.py`: Tests service functions like booking date formatting.

### ✅ Coverage

- **Route testing**:
    - Login with valid credentials
    - Booking creation and deletion
    - Profile editing and retrieval
    - Auth protection for protected routes

- **Error conditions**:
    - Access denied if not logged in
    - Invalid cleaner or booking ID

- **Backend services**:
    - Date formatting for booking display

- **Database logic**:
    - Verifies tables exist after init
    - Confirms admin account is seeded properly


