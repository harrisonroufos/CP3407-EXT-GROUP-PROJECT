# Iteration 1 plan
Assume:
> - 4 weeks per iteration
> - 20 business days per iteration
> - 0.4 velocity (team efficiency)
> - 4 developers 
> - `Total Development Days` = `business days per iteration` x `velocity` x `number of developers`
> - Total = 20 x 0.45 x 4

Hence, there are 36 days worth of user story development per iteration.

## Breakdown:
> Format: `link` |`estimated time` | `priority` (10 most important, 50 least)

**Development Tracker** - [MyClean](https://github.com/users/Casey-Summers/projects/1)

### Iteration 1
1. [Browse Cleaners](/user_stories/user_story_browse_cleaners.md) | 10 days | 10 - COMPLETE
2. [Cleaner Profile](/user_stories/user_story_create_cleaner_profile.md) | 6 days | 10 - COMPLETE
3. [Custom Cleaning Checklist](/user_stories/user_story_custom_cleaning_checklist.md) | 5 days | 20 - COMPLETE
4. [Customer Feedback and Reviews](/user_stories/user_story_customer_feedback.md) | 4 days | 20 - MOVED TO ITERATION 2
5. [Booking Confirmation](/user_stories/user_story_booking_confirmation.md) | 6.5 days | 30 - DROPPED
6. [Reliability Scores](/user_stories/user_story_reliability_scores.md) | 3 days | 20 - MOVED TO ITERATION 2

**Estimated Time - 34.5 days**

## Burn down chart
![Burn down chart](/iterations/images/iteration_1_burn_down_1.jpg)


# Iteration 2 plan
*We have changed the velocity based on iteration 1 outcome. We were able to complete 16.5 days of user stories which is about 0.2 velocity.

*We have also re-structed iteration 2 plan based velocity and priotiy adjustments. 

*A new user story was created called create booking, as this a key feature that we realized we had overlooked and thus was given a priority of 10.


Assume:
> - 4 weeks per iteration
> - 20 business days per iteration
> - 0.2 velocity (team efficiency)
> - 4 developers 
> - `Total Development Days` = `business days per iteration` x `velocity` x `number of developers`
> - Total = 20 x 0.2 x 4

Hence, there are 16 days worth of user story development per iteration.

### NEW Iteration 2 plan (based on iteration 1 summary)
1. [Create Booking](/user_stories/create_booking.md) | 5 days | 10 
2. [Customer Feedback](/user_stories/user_story_customer_feedback.md) | 4 days | 20 
3. [Reviews scores](/user_stories/user_story_reliability_scores.md) | 3 days | 30
4. [Job Cancellation](/user_stories/user_story_handle_cancellations.md) | 4 days | 30
   
**Estimated Time - 16 days**


### OLD Iteration 2
1. [Booking Reminders](/user_stories/user_story_booking_reminders.md) | 6.5 days | 20
2. [Clearner Availability](/user_stories/user_story_cleaner_availability) | 3 days | 20
3. [Recurring Job](/user_stories/user_story_recurring_job.md) | 5 days | 30
4. [Create Schedule](/user_stories/user_story_create_schedule.md) | 5 days | 30
5. [Job Cancellation](/user_stories/user_story_handle_cancellations.md) | 4 days | 30
6. [Schedule Notifications](/user_stories/user_story_schedule_notifications.md) | 3 days | 40
7. [Referral Program for Customers](/user_stories/user_story_referral_program_for_customers.md) | 4 days | 50

**Estimated Time - 30.5 days**



### Dropped User Stories (Deprioritised)
* [Route Mapping](/user_stories/user_story_efficient_route_mapping.md) - Found to be outside of project scope and required too many development days for length of iteration cycle.
* [Cleaning Supplies Tracker](/user_stories/user_story_cleaning_supplies_tracking.md) - Feature deemed unnecessary; product ordering outside of scope and cleaners have personal inventory logs. 
* [Chat With Cleaner](/user_stories/user_story_chat_with_hired_cleaner.md) - Most customers will be more familiar with existing chat apps that can be outsourced for free.
* [See Current Area Jobs](/user_stories/user_story_see_current_area_cleaning_jobs.md) - Iteration development cycle is too small to effectively incorporate location-based tracking and mapping.
* [Booking Reminders](/user_stories/user_story_booking_reminders.md) - Due to iteration 2 re-structure from iteration 1 summary.
* [Clearner Availability](/user_stories/user_story_cleaner_availability) - Due to iteration 2 re-structure from iteration 1 summary.
* [Recurring Job](/user_stories/user_story_recurring_job.md) - Due to iteration 2 re-structure from iteration 1 summary.
* [Create Schedule](/user_stories/user_story_create_schedule.md) - Due to iteration 2 re-structure from iteration 1 summary.
* [Schedule Notifications](/user_stories/user_story_schedule_notifications.md) - Due to iteration 2 re-structure from iteration 1 summary.
* [Referral Program for Customers](/user_stories/user_story_referral_program_for_customers.md) - Due to iteration 2 re-structure from iteration 1 summary.
* [Booking Confirmation](/user_stories/user_story_booking_confirmation.md) - Due to iteration 2 re-structure from iteration 1

 

# In progress:
> Format: `user story link` | `developer name` | `Task name` | `date started` <br>
> Use this area exclusively to track tasks that are in progress. Once they are complete, move them to the 'complete' section.


* [Create Booking](/user_stories/create_booking.md) | `Damon` | `Test and debug.` | --/--/----

# Completed:
> Format: `user story link` | `developer name` | `Task name` | `date Finished` <br>
* [Browse Cleaners](/user_stories/user_story_browse_cleaners.md) | `Casey` | `Research setting up the database and website.` | 18/02/2025
* [Browse Cleaners](/user_stories/user_story_browse_cleaners.md) | `Casey` & `Harrison` | `Develop the database for cleaners/users.` | 18/02/2025
* [Browse Cleaners](/user_stories/user_story_browse_cleaners.md) | `Daniel` | `Develop a UI to browse cleaners` | 22/02/2025
* [Browse Cleaners](/user_stories/user_story_browse_cleaners.md) | `Damon` | `Develop backend to get cleaners from database.` | 22/02/2025
* [Browse Cleaners](/user_stories/user_story_browse_cleaners.md) | `Casey` | `Test and debug.` | 22/02/2025


* [Cleaner Profile](/user_stories/user_story_create_cleaner_profile.md)  | `Harrison` | `Create a sign up page` | 28/2/2025
* [Cleaner Profile](/user_stories/user_story_create_cleaner_profile.md)  | `Casey` & `Harrison`  | `Implement backend to add new user to the database` | 28/2/2025
* [Cleaner Profile](/user_stories/user_story_create_cleaner_profile.md)  | `Daniel` | `Create UI for profile` | 07/03/2025
* [Cleaner Profile](/user_stories/user_story_create_cleaner_profile.md)  | `Damon` | `Display user infomation on user profile` | 02/03/2025
* [Cleaner Profile](/user_stories/user_story_create_cleaner_profile.md)  | `Casey` | `Test and debug` | 01/03/2025

* [Custom Cleaning Checklist](/user_stories/user_story_custom_cleaning_checklist.md) | `Casey` & `Damon`| `Develop UI for custom checklist creation.` | 14/03/2025
* [Custom Cleaning Checklist](/user_stories/user_story_custom_cleaning_checklist.md) | `Damon` | `Implement back end to store this checklist with a customer.` | 14/03/2025
* [Custom Cleaning Checklist](/user_stories/user_story_custom_cleaning_checklist.md) | `Casey` & `Damon` | `Test and debug.` | 15/03/2025

* [Create Booking](/user_stories/create_booking.md) | `Daniel` | `Develop UI for booking.` | 16/03/2025
* [Create Booking](/user_stories/create_booking.md) | `Harrison` | `Implement back end to store the booking.` | 15/03/2025
* [Create Booking](/user_stories/create_booking.md) | `Daniel` & `Harrison` | `Develop UI for dummy payment.` | 16/03/2025

* [Customer Feedback](/user_stories/user_story_customer_feedback.md) | `Casey` | `Create a survey form with various customer experience questions.` | 18/03/2025
* [Customer Feedback](/user_stories/user_story_customer_feedback.md) | `Casey` | `Design and integrate the survey form into the app.` | 18/03/2025
* [Customer Feedback](/user_stories/user_story_customer_feedback.md) | `Casey` | `Implement backend storage for customer reviews` | 18/03/2025


 
# Completed Maintenance and Feature Tasks
> Format: `developer name` | `Task name` | `date finished` <br>
* `Casey` | `Overhauled navigation menu` | 12/03/2025
* `Casey` | `Updated footer content and included About_Us` | 12/03/2025
* `Casey` | `Created About_Us page to explain MyClean` | 18/03/2025
* `Casey` | `Add view custom checklist to cleaner's booking page` | 18/03/2025
