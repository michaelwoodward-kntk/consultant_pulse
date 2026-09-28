Build: Consultant Pulse

Build a production-quality MVP called Consultant Pulse.

Consultant Pulse is an internal feedback and performance-evidence application for an IT consulting organization that delivers Databricks projects.

The application allows Technical Project Managers (TPMs) to quickly capture specific observations about consultants during projects. Managers can then view the accumulated evidence over time and use it to prepare performance reviews.

The core philosophy is:

«Capture evidence, not ratings.»

Do not build this as a traditional HR rating system. The system should record what happened, who observed it, when it happened, the project involved, the competency demonstrated, and the business/customer impact.

The application should make feedback collection take less than 1–2 minutes.

---

1. Technology

Use:

- Python
- Streamlit
- Databricks Apps
- Databricks SQL Warehouse
- Unity Catalog
- Delta tables
- SQL for data access
- Git-compatible project structure
- Environment variables/secrets for configuration
- Modular Python architecture

Design the application so that it can run locally for development with a configurable database connection, but its primary deployment target is Databricks Apps.

Do not introduce unnecessary frameworks or infrastructure.

Keep the initial implementation simple and maintainable.

---

2. Application Architecture

Use this conceptual architecture:

TPM
  |
  v
Streamlit App
  |
  v
Databricks SQL Warehouse
  |
  v
Unity Catalog / Delta Tables
  |
  +------------------+
  | |
  v v
Manager Review Builder
Dashboard

Future versions may add:

- Microsoft Teams integration
- AI-generated summaries
- Automated reminders
- Consultant self-reflection
- Project/customer outcome data

Do NOT implement those future features yet. Design the code so they can be added later.

---

3. Primary Users

There are three conceptual user types.

TPM

Can:

- View consultants associated with their projects
- Submit feedback
- View their own submitted feedback if permitted

Manager

Can:

- View consultants they manage
- View feedback about those consultants
- Filter feedback
- Review evidence by competency, project, TPM, and date
- Generate a performance-review evidence summary

Administrator

Can:

- Manage consultants
- Manage projects
- Manage project assignments
- Manage competency definitions

For the MVP, implement role-aware architecture even if authentication/authorization is initially simplified.

Do not hard-code a user's role into the application logic.

---

4. Core Data Model

Create the following Unity Catalog tables.

Assume a configurable catalog/schema:

${CATALOG}.${SCHEMA}

Do not hard-code production catalog names.

---

Table: consultants

Columns:

consultant_id STRING
name STRING
email STRING
role STRING
manager_id STRING
active_flag BOOLEAN
created_timestamp TIMESTAMP
updated_timestamp TIMESTAMP

Primary logical key:

consultant_id

---

Table: projects

Columns:

project_id STRING
project_name STRING
customer STRING
tpm_name STRING
tpm_email STRING
start_date DATE
end_date DATE
status STRING
created_timestamp TIMESTAMP
updated_timestamp TIMESTAMP

---

Table: project_assignments

This table establishes which consultants worked on which projects.

Columns:

consultant_id STRING
project_id STRING
assignment_role STRING
start_date DATE
end_date DATE
active_flag BOOLEAN

A consultant may work on multiple projects.

A project may have multiple consultants.

---

Table: competencies

Columns:

competency_id STRING
competency_name STRING
description STRING
display_order INT
active_flag BOOLEAN

Seed the table with:

TECHNICAL_EXPERTISE
CUSTOMER_IMPACT
DELIVERY_EXECUTION
COMMUNICATION
COLLABORATION
OWNERSHIP
LEADERSHIP
DATABRICKS_EXPERTISE
BUSINESS_ACUMEN

---

Table: feedback

This is the primary business table.

Columns:

feedback_id STRING
consultant_id STRING
project_id STRING
submitted_by_name STRING
submitted_by_email STRING
submitted_timestamp TIMESTAMP

feedback_type STRING
competency_id STRING

observation STRING
impact STRING
development_opportunity STRING

follow_up_required BOOLEAN

visibility STRING

created_timestamp TIMESTAMP
updated_timestamp TIMESTAMP

feedback_type values:

STRENGTH
DEVELOPMENT_OPPORTUNITY
RECOGNITION
CONCERN

visibility values:

MANAGER_ONLY
MANAGER_AND_CONSULTANT

Do not add an overall numeric rating.

---

5. Data Design Principles

The most important design principle is that feedback should capture specific evidence.

Avoid prompts such as:

«"Rate this consultant from 1–5."»

Instead ask:

«"What did the consultant actually do?"»

and:

«"What was the impact?"»

Bad example:

John is an excellent consultant.

Good example:

John took ownership of the customer's streaming architecture when
the original design was not meeting latency requirements.

Impact:

He worked with the customer's engineering team to redesign the
pipeline and helped return the project to schedule.

The application should encourage this type of evidence.

---

6. Screen 1 — TPM Feedback

Create a simple landing page.

Header:

Consultant Pulse

Subheader:

Capture project feedback while it's fresh.

Primary actions:

+ Give Feedback
+ Recognize Someone
View My Feedback

For the MVP, "Recognize Someone" can simply open the same feedback form with feedback_type preselected as RECOGNITION.

---

Feedback Form

Fields:

Consultant

Dropdown populated from active consultants.

Label:

Consultant

Required.

---

Project

Dropdown populated from projects associated with the selected consultant.

Required.

---

Competency

Dropdown or selectable cards.

Display:

Technical Expertise
Customer Impact
Delivery / Execution
Communication
Collaboration
Ownership
Leadership
Databricks Expertise
Business Acumen

Required.

---

Feedback Type

Options:

Strength
Development Opportunity
Recognition
Concern

Required.

---

What happened?

Large text area.

Prompt text:

What did the consultant actually do?

Helper text:

Describe a specific action, behavior, decision, or accomplishment.

Required.

---

What was the impact?

Large text area.

Prompt:

What was the result or impact?

Helper text:

Consider customer impact, delivery impact, technical impact,
team impact, or business outcome.

Required.

---

Development Opportunity

Optional text area.

Only display this field prominently when feedback_type is:

DEVELOPMENT_OPPORTUNITY
CONCERN

Prompt:

What could the consultant do differently or improve?

---

Follow-up Required

Boolean:

Does this require manager follow-up?

Default:

false

---

Visibility

Default:

MANAGER_ONLY

Do not expose consultant-visible feedback functionality unless the architecture supports it cleanly.

---

Submit

Button:

Submit Feedback

After successful submission display:

Feedback captured.

Thank you for taking a moment to document the observation.

Then provide:

Submit Another
Return Home

---

7. UX Requirements for Feedback

The feedback form should feel fast.

Avoid:

- unnecessary fields
- complex navigation
- multi-page forms
- excessive validation
- numeric ratings
- long surveys

Use:

- sensible defaults
- dropdowns
- clear labels
- helpful placeholder text
- immediate validation
- confirmation after submission

Target completion time:

< 2 minutes

---

8. Screen 2 — Manager Dashboard

Create:

Manager Dashboard

Display cards:

My Consultants
Active Projects
Feedback This Period
Consultants Without Recent Feedback

Then display a consultant table.

Columns:

Consultant
Role
Active Projects
Feedback Count
Last Feedback
Strengths
Development Opportunities

Allow filtering by:

Date Range
Consultant
Project
Competency
Feedback Type
TPM

Clicking a consultant opens the Consultant Detail page.

---

9. Screen 3 — Consultant Detail

Header:

John Smith
Senior Consultant

Summary cards:

Projects
Feedback Observations
TPMs Providing Feedback
Last Feedback

Then display competency activity.

Example:

Technical Expertise 8
Customer Impact 6
Delivery 5
Communication 3
Leadership 4

Do NOT present these as performance scores.

They represent the number of documented observations.

Clearly label the visualization:

Documented Observations

not:

Performance Score

---

10. Feedback Timeline

Display a chronological timeline of observations.

Example:

September 18, 2026
Customer ABC
Jane Doe — TPM

Technical Leadership

Took ownership of the streaming architecture...

Impact:
Helped reduce latency and return the project to schedule.

Then:

August 27, 2026
Customer XYZ
Mark Jones — TPM

Customer Impact

...

Allow filtering by:

Date
Project
Competency
Feedback Type
TPM

---

11. Screen 4 — Performance Review Evidence

Create a page:

Performance Review Evidence

Inputs:

Consultant
Review Period

Example:

Consultant: John Smith
Period: 2026

Display sections:

Technical Expertise

Show documented observations.

Customer Impact

Show documented observations.

Delivery / Execution

Show documented observations.

Communication

Show documented observations.

Collaboration

Show documented observations.

Leadership

Show documented observations.

Databricks Expertise

Show documented observations.

Business Acumen

Show documented observations.

Development Opportunities

Show documented development observations.

Each observation must retain its source metadata:

Date
Project
TPM
Competency

The manager should be able to trace every summary statement back to actual feedback.

---

12. Review Evidence Summary

Create a button:

Build Evidence Summary

For MVP, do NOT require an LLM.

Generate a structured summary using the database records.

Example:

2026 Performance Evidence
John Smith

Technical Expertise
--------------------
5 documented observations across 3 projects.

Customer Impact
----------------
4 documented observations across 2 projects.

Leadership
------------
3 documented observations across 3 projects.

Development Opportunities
--------------------------
2 observations referenced proactive communication during
project transitions.

The summary must distinguish between:

number of observations

and

actual performance conclusions.

Do not automatically label someone "high performing," "low performing," etc.

The manager makes that judgment.

---

13. Future AI Architecture

Prepare an abstraction layer for a future:

ReviewSummaryService

with a method conceptually like:

generate_review_summary(
    consultant_id,
    start_date,
    end_date
)

The initial implementation can be deterministic.

Later this service can use an LLM.

When AI is eventually implemented, it must:

1. Retrieve only feedback relevant to the consultant and review period.
2. Group evidence by competency.
3. Generate a summary grounded only in the retrieved evidence.
4. Preserve source references.
5. Never invent accomplishments.
6. Never create performance ratings.
7. Clearly distinguish observations from conclusions.
8. Allow the manager to edit the generated content.

The architecture should make this future extension straightforward.

---

14. Security

Use Unity Catalog permissions where appropriate.

The application must not expose all consultant feedback to every user.

Conceptual access:

TPM:

Can submit feedback.
Can see appropriate project/consultant data.

Manager:

Can view consultants they manage.
Can view their feedback evidence.

Administrator:

Can manage reference data.

Do not rely solely on hiding UI elements for security.

Data access should also be enforced at the query/data layer.

Create a centralized authorization module rather than scattering permission checks throughout the application.

---

15. Configuration

Use environment variables or Databricks App configuration for:

DATABRICKS_HOST
DATABRICKS_WAREHOUSE_ID
DATABRICKS_CATALOG
DATABRICKS_SCHEMA

Do not commit credentials.

Do not hard-code tokens.

Create:

.env.example

but never commit a real .env file.

---

16. Project Structure

Use a structure similar to:

consultant-pulse/
|
├── app.py
|
├── pages/
│ ├── feedback.py
│ ├── dashboard.py
│ ├── consultant.py
│ └── review.py
|
├── services/
│ ├── feedback_service.py
│ ├── consultant_service.py
│ ├── project_service.py
│ ├── review_service.py
│ └── authorization.py
|
├── data/
│ ├── connection.py
│ ├── queries.py
│ └── schema.sql
|
├── models/
│ ├── consultant.py
│ ├── project.py
│ └── feedback.py
|
├── utils/
│ ├── validation.py
│ └── formatting.py
|
├── tests/
│ ├── test_feedback.py
│ ├── test_services.py
│ └── test_validation.py
|
├── requirements.txt
├── app.yaml
├── README.md
└── .env.example

Adjust this structure if a simpler architecture is clearly better, but maintain separation between:

UI
business logic
data access
authorization

---

17. Database Initialization

Create SQL scripts that can initialize:

consultants
projects
project_assignments
competencies
feedback

Include seed data for development.

Use generated sample consultants such as:

Alex Morgan
Chris Davis
Jamie Wilson
Taylor Brown

Use sample projects:

Customer ABC
Customer XYZ
Customer 123

Do not use real employee/customer data in seed data.

---

18. Validation

Required:

consultant
project
competency
feedback type
observation
impact

Prevent empty or whitespace-only submissions.

Provide friendly validation messages.

Generate feedback_id automatically.

Use UTC timestamps in the database.

Display timestamps in the user's local timezone when practical.

---

19. Error Handling

Do not expose raw database errors to users.

Instead show messages such as:

We couldn't save the feedback.
Please try again or contact support.

Log technical details for troubleshooting.

Handle:

- database connection failure
- query failure
- missing reference data
- invalid consultant/project combination
- duplicate submission
- authorization failure

---

20. Observability

Create basic application logging.

Log:

application startup
database connection errors
feedback submission success/failure
authorization failures
unexpected exceptions

Do not log sensitive feedback text unnecessarily.

---

21. Testing

Create unit tests for:

- feedback validation
- consultant/project relationship
- feedback creation
- filtering
- review-period selection
- authorization logic

Also provide a simple smoke-test checklist in README.md.

---

22. Development Experience

The README must explain:

1. How to configure local development.
2. How to configure the Databricks SQL Warehouse.
3. How to create the Unity Catalog schema.
4. How to initialize the tables.
5. How to run locally.
6. How to deploy as a Databricks App.
7. How to configure environment variables.
8. How to run tests.

Include example commands where appropriate.

---

23. Databricks Deployment

Create an appropriate Databricks Apps configuration.

The application should be deployable through Git.

Structure the project so that it can eventually be integrated into CI/CD.

Do not implement a complicated CI/CD pipeline in the MVP.

At minimum, make the repository clean and deployment-ready.

---

24. UI Design

Use a professional internal enterprise application aesthetic.

Prioritize:

- clean layout
- whitespace
- clear typography
- simple navigation
- restrained use of color
- responsive layout
- obvious primary actions

Do not make it look like an HR administrative system.

It should feel like a modern internal product.

Suggested navigation:

Home
Give Feedback
My Dashboard
Consultants
Review Evidence
Admin

Only show navigation items appropriate to the user's role.

---

25. Important Product Principles

Follow these principles throughout implementation.

Principle 1 — Evidence over ratings

Never introduce a 1–5 consultant rating unless explicitly requested later.

Principle 2 — Specific observations

Encourage concrete examples.

Principle 3 — Business impact

Capture why the behavior mattered.

Principle 4 — Low friction

TPMs should be able to provide useful feedback in under two minutes.

Principle 5 — Traceability

Every performance-review statement should ultimately trace back to source observations.

Principle 6 — Manager judgment

The system provides evidence. The manager makes the performance assessment.

Principle 7 — Historical value

Feedback should accumulate over time and remain useful months later.

Principle 8 — Extensibility

Design for future Teams integration and AI summarization without implementing them now.

---

26. Build Order

Implement in this order.

Phase 1 — Foundation

1. Create repository structure.
2. Create configuration.
3. Create database connection.
4. Create SQL schema.
5. Create seed data.
6. Create data-access layer.
7. Create models/services.

Phase 2 — Feedback

8. Build feedback form.
9. Implement validation.
10. Implement feedback submission.
11. Add confirmation.
12. Add feedback history.

Phase 3 — Manager Experience

13. Build manager dashboard.
14. Build consultant detail.
15. Build competency observation counts.
16. Build feedback timeline.
17. Add filtering.

Phase 4 — Review Evidence

18. Build review-period selector.
19. Group observations by competency.
20. Build evidence summary.
21. Add export/copy capability.

Phase 5 — Hardening

22. Add authorization.
23. Add error handling.
24. Add logging.
25. Add tests.
26. Improve UI.
27. Document deployment.

---

27. Definition of Done

The MVP is complete when:

- A TPM can select a consultant and project.
- A TPM can submit a specific observation in under two minutes.
- Feedback is stored in Delta/Unity Catalog.
- A manager can see all feedback for their consultants.
- Feedback can be filtered by consultant, project, competency, TPM, and date.
- A manager can view a consultant's evidence timeline.
- A manager can select a review period.
- The system groups documented evidence by competency.
- The manager can see the source of every observation.
- No numeric performance ratings are required.
- Role-aware architecture exists.
- The application can run as a Databricks App.
- No credentials are committed.
- Tests exist for core business logic.
- README documentation exists.

---

28. How to Work

Act as a senior full-stack engineer who also understands Databricks.

Before writing code:

1. Inspect the repository.
2. Identify existing files and conventions.
3. Identify anything that can be reused.
4. Produce a short implementation plan.
5. Then implement the MVP.

Do not over-engineer.

Prefer simple, readable code over abstractions that don't provide immediate value.

When there are architectural choices, favor the solution that is:

simplest
Databricks-native
maintainable
secure
easy to extend

Build the application incrementally and keep it runnable after each major phase.

At the end, provide:

- files created/modified
- setup instructions
- database initialization instructions
- local run instructions
- Databricks App deployment instructions
- tests implemented
- known limitations
- recommended next steps

Do not implement future features simply because they are mentioned in the design. Keep the MVP focused.I'd paste that into Cursor at the root of a new Git repo and let it first inspect the environment and produce the implementation plan before asking it to start coding.

One additional recommendation: because this is a performance-management system, I'd keep the first version intentionally conservative around access controls and auditability. The feedback itself is more sensitive than the technical architecture suggests, so getting the Unity Catalog permissions and manager/TPM visibility model right is more important than adding AI early.