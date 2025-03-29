# Iteration 2 Plan

We have changed the velocity based on Iteration 1 outcome. We were able to complete 16.5 days of user stories, which is about 0.2 velocity.

We also restructured the Iteration 2 plan based on these findings. A new user story was created: "Create Booking" — a critical feature that was originally overlooked.

## Assumptions:
> - 4 weeks per iteration  
> - 20 business days per iteration  
> - 0.2 velocity (team efficiency)  
> - 4 developers
> - `Total Development Days` = `business days per iteration` x `velocity` x `number of developers`  
> - Total = 20 x 0.2 x 4 = 16 days

## Breakdown:
> Format: `link` | `estimated time` | `priority` (10 most important, 50 least)

> [!Note]
> **GitHub Project Page** - [Development Tracker](https://github.com/users/Casey-Summers/projects/1) <br>
> **GitHub Project Version History** - [Project Iterations](/major_component_designs/github_pages_timeline.md)

1. [Create Booking](/user_stories/user_story_create_booking.md) | 5 days | 10 - COMPLETED
2. [Send Feedback and Reviews](/user_stories/user_story_send_feedback_and_reviews.md) | 4 days | 20 - COMPLETED
3. [Show Cleaner Reliability Scores](/user_stories/user_story_show_cleaner_reliability_scores.md) | 3 days | 30 - COMPLETED
4. [Cancel Booking](/user_stories/user_story_handle_cancel_booking.md) | 4 days | 30 - COMPLETED

**Estimated Time - 16 days**

## Burn down chart
![Burn down chart](/iterations/images/iteration_2_burndown.jpg)

---

# In Progress:
> Format: `user story link` | `developer name` | `Task name` | `date started`

(Empty at the end of Iteration 2)

---

## Dropped / Deprioritised User Stories
* [Route Mapping](/user_stories/user_story_efficient_route_mapping.md)  
* [Cleaning Supplies Tracker](/user_stories/user_story_cleaning_supplies_tracking.md)  
* [Chat With Cleaner](/user_stories/user_story_chat_with_hired_cleaner.md)  
* [See Current Area Jobs](/user_stories/user_story_see_current_area_cleaning_jobs.md)  
* [Booking Reminders](/user_stories/user_story_booking_reminders.md)  
* [Cleaner Availability](/user_stories/user_story_cleaner_availability.md)  
* [Recurring Job](/user_stories/user_story_recurring_job.md)  
* [Create Schedule](/user_stories/user_story_create_schedule.md)  
* [Schedule Notifications](/user_stories/user_story_schedule_notifications.md)  
* [Referral Program for Customers](/user_stories/user_story_referral_program_for_customers.md)  
* [Receive Booking Confirmation](/user_stories/user_story_receive_booking_confirmation.md) – revised and implemented as on-screen confirmation only

---

## Completed
> Format: `user story link` | `developer name` | `Task name` | `date finished`

* [Create Booking](/user_stories/user_story_create_booking.md) | `Daniel` | Develop UI for booking. | 16/03/2025  
* [Create Booking](/user_stories/user_story_create_booking.md) | `Harrison` | Implement backend to store the booking. | 15/03/2025  
* [Create Booking](/user_stories/user_story_create_booking.md) | `Daniel` & `Harrison` | Develop UI for dummy payment. | 16/03/2025  
* [Create Booking](/user_stories/user_story_create_booking.md) | `Damon`, `Harrison`, `Casey` | Test and debug. | 18/03/2025  

* [Send Feedback and Reviews](/user_stories/user_story_send_feedback_and_reviews.md) | `Casey` | Create a survey form | 18/03/2025  
* [Send Feedback and Reviews](/user_stories/user_story_send_feedback_and_reviews.md) | `Casey` | Integrate survey form into app | 18/03/2025  
* [Send Feedback and Reviews](/user_stories/user_story_send_feedback_and_reviews.md) | `Casey` | Implement backend storage | 18/03/2025  
* [Send Feedback and Reviews](/user_stories/user_story_send_feedback_and_reviews.md) | `Damon` | Display ratings on profile | 21/03/2025  
* [Send Feedback and Reviews](/user_stories/user_story_send_feedback_and_reviews.md) | `Damon`, `Casey` | Test and debug | 21/03/2025  

* [Show Cleaner Reliability Scores](/user_stories/user_story_show_cleaner_reliability_scores.md) | `Damon` | Backend system for reliability | 19/03/2025  
* [Show Cleaner Reliability Scores](/user_stories/user_story_show_cleaner_reliability_scores.md) | `Damon` | Display reliability scores | 20/03/2025  
* [Show Cleaner Reliability Scores](/user_stories/user_story_show_cleaner_reliability_scores.md) | `Damon`, `Casey` | Test and debug | 23/03/2025  

* [Cancel Booking](/user_stories/user_story_handle_cancel_booking.md) | `Harrison`, `Casey` | Develop job database | 20/03/2025  
* [Cancel Booking](/user_stories/user_story_handle_cancel_booking.md) | `Daniel` | Develop UI | 22/03/2025  
* [Cancel Booking](/user_stories/user_story_handle_cancel_booking.md) | `Daniel` | Test and Debug | 24/03/2025  

# Completed Maintenance and Feature Tasks (Iteration 2)
> Format: `developer name` | `Task name` | `date finished`

* `Casey` | Created About_Us page to explain MyClean | 18/03/2025  
* `Casey` | Add view custom checklist to cleaner's booking page | 18/03/2025
* `Casey` | Refactored the 'initialise database' function into logical sections (SRP) | 23/03/2025
