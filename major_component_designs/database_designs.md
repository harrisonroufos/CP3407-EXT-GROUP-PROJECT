# Database Designs for CP3407's 'MyClean' solution.

---

### MyClean Database Design (Explanation below)
![database diagram](/database_files/myclean_database_diagram.png)

---

## Justification and Explanation of the MyClean Database Design and Implementation
The MyClean application is a full-stack web platform built using Flask and hosted on Render, integrating a PostgreSQL database for persistent storage. The database design reflects a clean, modular structure aligned with Flask development patterns and secure deployment considerations.

### Hosting Environment and Deployment
The application is cloud-hosted on Render, which runs both the Flask web service and a managed PostgreSQL database instance. Environment-specific settings (like `DATABASE_URL`) are injected via environment variables, allowing seamless transitions between local SQLite development and live PostgreSQL deployment. This dual-mode approach is supported through conditional logic in `app.py`, particularly in the database connection and table creation layers.

### Database Structure and Normalisation

The schema is normalised into logical entities that map directly to the domain model of MyClean:

| Table                 | Description                                                                 |
|-----------------------|-----------------------------------------------------------------------------|
| `users`               | Central login identity for all accounts (cleaners and customers)            |
| `customers`, `cleaners` | Extend `users` via foreign keys, supporting role separation                 |
| `bookings`            | Represents jobs between cleaners and customers                              |
| `checklists`          | Tied to specific bookings; contains task lists per job                      |
| `customer_checklists` | Optional pre-saved checklist templates created by customers                 |
| `reviews`             | Feedback left by customers, structured into four questions and rating       |

This modularisation ensures:
- Role-based access and logic (session checks for `cleaner_id` vs `customer_id`)
- Easy maintenance and scalability
- Foreign key enforcement and referential integrity

---

### Integration with Flask Routes
The structure of the database supports the full range of routes in `app.py`, including:

- **Authentication and Authorisation**  
  `signup`, `login`, and session management directly map to the `users` table, with additional role lookups in `customers` and `cleaners`.

- **Bookings and Scheduling**  
  The `/book/<int:cleaner_id>` route inserts into `bookings`, linking both user types. Checklist data can be optionally provided at booking time, inserted into `checklists`.

- **Checklist Management**  
  Custom checklists are stored per customer via `/custom_checklist`, allowing reuse across bookings. This logic is supported by `customer_checklists` and conditional inserts or updates depending on whether a record already exists.

- **Review System**  
  The `/submit_review` endpoint inserts structured feedback directly into `reviews`. It supports both numeric scores and qualitative input, stored in distinct columns.

- **Dynamic Data Loading**  
  Routes like `/show_cleaners` and `/manage_bookings` dynamically query the database and format the results into dictionaries for rendering with Jinja2 templates. These routes support both PostgreSQL and SQLite using placeholder logic (`%s` vs `?`) for parameterised queries.

---

### Render Hosting and Cloud DB Compatibility
The app leverages environment detection to toggle between local SQLite and Render-hosted PostgreSQL, supported by:

- The `DATABASE_URL` environment variable
- Modular query structures and creation logic
- Schema compatibility for both database types (e.g., `SERIAL` vs `AUTOINCREMENT`, `JSON` vs `TEXT` for checklist items)

This flexibility ensures that developers can test features locally while preserving full production parity.

---

### Security and Best Practices
- Passwords are hashed using `werkzeug.security`
- Queries use parameter placeholders to mitigate SQL injection
- Session variables are type-checked to control access to user-specific routes
- Table creation and admin user population occur at the same time, ensuring proper startup routines across all deployment types

---

### Summary
The MyClean database solution has:

- Logical, normalised schema supporting all application features
- Environment-aware deployment strategy using Flask and Render
- Flexible data access and user flow logic across customers, cleaners, and administrators
- Compatibility with modern web application standards, including cloud deployment, user feedback, and dynamic content rendering
