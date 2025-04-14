# CP3407 External Group 1

## Team Members

- Harrison Roufos
- Damon Lindsay
- Casey Summers
- Daniel Brooks

---

## Iteration Plans

| Iteration                                       | Duration  | Details                                                  |
|-------------------------------------------------|-----------|----------------------------------------------------------|
| [Iteration 1](./iterations/iteration_1_plan.md) | 3-4 weeks | Focus on core booking, profiles, and feedback            |
| [Iteration 2](./iterations/iteration_2_plan.md) | 3-4 weeks | Focus on reliability, checklists, cancellations, mockups |

## Major Components

| Component           | Description                                                       | Link                                             |
|---------------------|-------------------------------------------------------------------|--------------------------------------------------|
| Architectural Designs | Describes system structure, components, and deployment layers   | [View](major_component_designs/architectural_designs.md)               |
| Database Designs    | Explains the relational database schema and justification         | [View](major_component_designs/database_designs.md)                    |
| GitHub Pages Timeline | Tracks key development milestones and iteration progress        | [View](major_component_designs/github_pages_timeline.md)               |
| Interface Designs   | Compares wireframes and final interface designs                   | [View](major_component_designs/interface_designs.md)                   |

## User Stories

| Area                | Description                                                       | Link                                             |
|---------------------|-------------------------------------------------------------------|--------------------------------------------------|
| Userstories Directory | Lists all completed and dropped user stories                    | [View](user_stories)               |

---

## Live Website
You can use the cloud-hosted website by visiting: [https://cp3407-myclean.onrender.com/](https://cp3407-myclean.onrender.com/)

> [!Note]  
> The website is hosted on [Render](https://render.com), a cloud-based deployment platform that connects 'MyClean' application with an external Postgre 16.0, Oregon (US West) database.
> Because Render puts inactive sites to sleep to save resources, the site may take **10–30 seconds** to start when accessed for the first time.

> Alternatively: <br>
> Open the code in a local environment, run `app.py`, and visit the local IP shown in the terminal.
>  
> The application is built using Flask (Python) and is deployed as a full-stack web service. It connects directly to a managed PostgreSQL database, also hosted on Render.
> This enables full functionality, including user login, profile management, and data storage, without requiring any local setup.

> [!Important]
> The local environment offers a toggle between a local testing database and the production cloud-hosted one. You can toggle between using them by changing the value of `USE_LOCAL_DB` by following the path `Backend/services/.env`. This feature was used frequently for testing purposes throughout development.

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

## 📋 Completed User Stories

| User Story                         | Iteration | Priority | Status     | Link                                                                     |
|-----------------------------------|-----------|----------|------------|--------------------------------------------------------------------------|
| Create Booking                    | 1         | 10       | ✅ Complete | [View](./user_stories/user_story_create_booking.md)                      |
| Receive Booking Confirmation      | 1         | 20       | ✅ Complete | [View](./user_stories/user_story_receive_booking_confirmation.md)        |
| Browse Cleaners                   | 1         | 30       | ✅ Complete | [View](./user_stories/user_story_browse_cleaners.md)                     |
| Create Custom Cleaning Checklist  | 1         | 40       | ✅ Complete | [View](./user_stories/user_story_create_custom_cleaning_checklist.md)    |
| Display Cleaner Profile           | 1         | 40       | ✅ Complete | [View](./user_stories/user_story_display_cleaner_profile.md)             |
| Show Cleaner Reliability Scores   | 2         | 20       | ✅ Complete | [View](./user_stories/user_story_show_cleaner_reliability_scores.md)     |
| Send Feedback and Reviews         | 2         | 25       | ✅ Complete | [View](./user_stories/user_story_send_feedback_and_reviews.md)           |
| Cancel Booking                    | 2         | 30       | ✅ Complete | [View](./user_stories/user_story_handle_cancel_booking.md)               |


---

## ❌ Dropped / Deprioritized User Stories

| User Story                    | Iteration | Priority | Status     | Link                                                                |
|------------------------------|-----------|----------|------------|---------------------------------------------------------------------|
| Cleaner Availability         | 2         | 20       | ❌ Dropped | [View](./user_stories/user_story_cleaner_availability.md)           |
| Referral Program             | 2         | 20       | ❌ Dropped | [View](./user_stories/user_story_referral_program_for_customers.md) |
| Chat With Hired Cleaner      | 2         | 25       | ❌ Dropped | [View](./user_stories/user_story_chat_with_hired_cleaner.md)        |
| Cleaning Supplies Tracking   | 2         | 30       | ❌ Dropped | [View](./user_stories/user_story_cleaning_supplies_tracking.md)     |
| Create Schedule              | 2         | 30       | ❌ Dropped | [View](./user_stories/user_story_create_schedule.md)                |
| Booking Reminders            | 2         | 30       | ❌ Dropped | [View](./user_stories/user_story_booking_reminders.md)              |
| Efficient Route Mapping      | 2         | 40       | ❌ Dropped | [View](./user_stories/user_story_efficient_route_mapping.md)        |
| Schedule Notifications       | 2         | 40       | ❌ Dropped | [View](./user_stories/user_story_schedule_notifications.md)         |
| Recurring Job                | 2         | 50       | ❌ Dropped | [View](./user_stories/user_story_recurring_job.md)                  |
| See Current Area Jobs        | 2         | 50       | ❌ Dropped | [View](./user_stories/user_story_see_current_area_cleaning_jobs.md) |

---

# Database Diagram

![database diagram](/database_files/myclean_database_diagram.png)

---

# UML Diagram

![uml diagram](/database_files/myclean_uml_diagram.png)

---

## 🖼️ Interface Design & UI Mockups

All designs (including those for dropped features) can be seen and compared within the [Interface Designs](major_component_designs/interface_designs.md) directory.  
Each mockup is linked within its respective user story, but this allows you to browse them all in one place.

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

We implemented comprehensive testing using `pytest` across all major components of the system. They can be found in the [Tests](/tests) directory. Our tests cover:

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


