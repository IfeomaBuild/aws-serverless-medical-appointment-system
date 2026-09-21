# AWS Serverless Medical Appointment System

A fully serverless medical appointment booking application built on AWS. The project demonstrates how a static web frontend can integrate with managed AWS services to retrieve appointment availability, create bookings safely, prevent double booking, and send confirmation emails.

## Project Overview

The goal of this project was to build an end-to-end appointment booking workflow without managing traditional servers.

A patient uses the web interface to select an appointment date and available time slot, enters their details, and submits the booking. The backend validates availability before accepting the appointment. Once a booking succeeds, the appointment is stored and an email confirmation is sent to the patient.

The completed system was tested successfully: appointments could be booked, already-booked slots were protected against duplicate booking, and confirmation emails were delivered.

## Key Features

- Serverless architecture on AWS
- Responsive static web frontend
- Retrieval of available appointment slots
- Appointment booking through API endpoints
- Prevention of double booking using DynamoDB conditional writes
- Persistent appointment data
- Email confirmation after successful booking
- Static frontend hosting using Amazon S3
- Global frontend delivery using Amazon CloudFront
- Private S3 origin access through CloudFront
- HTTPS delivery through CloudFront
- IAM-based permissions between AWS services

## AWS Services Used

| Service | Purpose |
| --- | --- |
| Amazon S3 | Stores the static frontend files |
| Amazon CloudFront | Securely delivers the frontend and provides HTTPS/CDN distribution |
| Amazon API Gateway | Exposes backend HTTP API endpoints |
| AWS Lambda | Executes appointment availability and booking logic |
| Amazon DynamoDB | Stores appointment data and protects appointment slots from duplicate booking |
| Amazon SES | Sends appointment confirmation emails |
| AWS IAM | Controls permissions between services |
| Amazon CloudWatch | Supports logging and troubleshooting of serverless functions |

## Architecture

```text
                         AWS Serverless Medical Appointment System

+------------------+
| Patient / Browser|
+--------+---------+
         |
         | HTTPS
         v
+------------------+
| Amazon CloudFront|
| CDN + HTTPS      |
+--------+---------+
         |
         v
+------------------+
| Amazon S3        |
| HTML / CSS / JS  |
+--------+---------+
         |
         | REST API requests
         v
+------------------+
| API Gateway      |
+--------+---------+
         |
         +-----------------------------+
         |                             |
         v                             v
+----------------------+      +----------------------+
| Get Available Slots  |      | Book Appointment     |
| Lambda               |      | Lambda               |
+----------+-----------+      +----------+-----------+
           |                             |
           | read bookings               | conditional write
           v                             v
       +-------------------------------------+
       | Amazon DynamoDB                     |
       | MedicalAppointment                  |
       | SlotID = Doctor#Date#Time           |
       +-------------------------------------+
                                             |
                                             | after successful booking
                                             v
                                  +----------------------+
                                  | Amazon SES           |
                                  | Confirmation Email   |
                                  +----------------------+
```

### Architecture Responsibilities

**CloudFront + S3** form the presentation layer. S3 stores `index.html`, `style.css`, and `script.js`, while CloudFront provides the public HTTPS entry point and securely accesses the private S3 origin.

**API Gateway** forms the API layer. The browser sends requests for appointment availability and appointment creation to API endpoints, which invoke the appropriate Lambda function.

**AWS Lambda** forms the application layer. One function calculates available appointment slots and another processes bookings.

**DynamoDB** forms the persistence layer. Appointment slots are represented using a `SlotID` composed from doctor, date, and time. The booking function uses a conditional database write so the same slot cannot be successfully created twice.

**Amazon SES** provides the notification layer. After a booking succeeds, the application sends the patient an appointment confirmation email containing the appointment details.

## Application Flow

1. The patient opens the application through CloudFront.
2. CloudFront retrieves the static frontend from the private S3 origin.
3. The patient selects a date.
4. JavaScript calls the available-slots API through API Gateway.
5. API Gateway invokes the Get Available Slots Lambda function.
6. Lambda checks DynamoDB and removes already-booked times from the clinic schedule.
7. The available times are returned to the browser.
8. The patient selects a time and submits their name and email address.
9. API Gateway invokes the Book Appointment Lambda function.
10. The Lambda function generates an appointment ID and attempts a DynamoDB conditional write.
11. If the `SlotID` already exists, DynamoDB rejects the write and the API returns a conflict response, preventing double booking.
12. If the write succeeds, the appointment is stored with `CONFIRMED` status.
13. Amazon SES sends the appointment confirmation email.
14. The API returns the successful booking result to the frontend.

## Frontend Deployment

The frontend consists of:

```text
index.html
script.js
style.css
```

These files were uploaded to a dedicated Amazon S3 bucket.

Instead of exposing the bucket directly as a public website, Amazon CloudFront was configured in front of S3. CloudFront was granted access to the private S3 origin, allowing the bucket itself to remain restricted while the application is delivered through CloudFront.

The CloudFront distribution was configured with `index.html` as the default root object.

## Double-Booking Prevention

One of the most important requirements was ensuring that two users could not successfully reserve the same appointment slot.

Each appointment uses a slot identifier in the following form:

```text
DoctorID#AppointmentDate#AppointmentTime
```

For example:

```text
DOCTOR001#2026-10-22#11:30
```

The booking Lambda writes the appointment with a DynamoDB condition requiring `SlotID` not to already exist. This makes the protection atomic at the database layer instead of relying on the frontend's displayed availability.

If another request attempts to reserve the same slot, DynamoDB raises a conditional-check failure and the API returns HTTP `409`, indicating that the appointment is already booked.

Testing confirmed that a successfully booked appointment could not subsequently be booked again.

## Appointment Availability

The Get Available Slots Lambda contains the clinic schedule and accepts a date and doctor ID through query parameters.

It validates the date, rejects weekend appointments, checks the stored appointment SlotIDs for that doctor and date, and removes booked times before returning `availableSlots` to the frontend.

The current implementation uses a DynamoDB `Scan` operation. This is suitable for the scale of this demonstration project, but a production version should use a DynamoDB data model and index that supports an efficient `Query` for doctor/date availability.

## Email Confirmation

After a successful booking, the backend integrates with Amazon SES to send an email confirmation to the patient. The confirmation contains the generated appointment ID, doctor, appointment date, and appointment time.

During testing, the complete workflow succeeded from the web interface through the backend and database to the final confirmation email.

## Challenges Encountered

Building the project involved more than simply connecting AWS services. Several integration points required troubleshooting and validation.

### API and Lambda integration

The Lambda functions had to correctly process requests coming from API Gateway and return responses in a format the browser could consume.

### CORS and browser communication

Because the frontend and API are separate resources, browser requests required the correct cross-origin configuration. This was an important part of getting the deployed frontend to communicate reliably with the backend.

### Appointment availability

The application needed to return only valid available slots rather than simply accepting whatever appointment time was submitted from the frontend.

### Preventing duplicate appointments

A simple read-then-write workflow can create race conditions. Booking protection therefore needed to exist at the backend/database layer rather than depending on frontend state alone. DynamoDB conditional writes solved this requirement.

### Email delivery

The booking workflow also had to integrate correctly with Amazon SES so that confirmation messages were sent as part of a successful appointment flow.

### Frontend deployment

The frontend was prepared as static HTML, CSS, and JavaScript files and uploaded to S3. CloudFront was then configured with S3 as its origin, private bucket access enabled, recommended origin/cache settings, and `index.html` as the default root object.

## Testing and Results

End-to-end testing verified the core requirements:

- The deployed frontend loaded successfully through CloudFront.
- Available appointment slots were retrieved.
- Weekend appointment dates were rejected by the availability function.
- A patient could submit a valid appointment.
- Successful appointments were persisted in DynamoDB.
- A previously booked slot could not be booked again successfully.
- A confirmation email was received after a successful booking.
- The frontend was successfully deployed through Amazon S3 and CloudFront.

## What I Learned

This project provided practical experience with designing and troubleshooting a multi-service AWS serverless application. Key lessons included:

- Designing serverless application flows
- Integrating API Gateway with Lambda
- Working with DynamoDB for application state
- Using conditional writes to protect data integrity
- Configuring IAM permissions between AWS services
- Troubleshooting CORS between a browser frontend and an API
- Integrating transactional email with Amazon SES
- Hosting static applications in S3
- Using CloudFront with a private S3 origin
- Testing an application as a complete end-to-end system
- Recognizing when a DynamoDB access pattern should evolve from `Scan` to `Query`

## Security Considerations

The project keeps infrastructure exposure limited where possible. The S3 frontend origin is accessed through CloudFront instead of requiring the bucket to be generally public. IAM permissions should follow least-privilege principles, and AWS credentials or secrets must never be committed to this repository.

For a production medical system, additional controls would be required before storing or processing real patient health information, including appropriate authentication, authorization, encryption, auditing, data-retention policies, regulatory/compliance review, and operational monitoring.

## Repository Structure

```text
aws-serverless-medical-appointment-system/
├── README.md
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── script.js
├── lambda/
│   ├── book-appointment/
│   │   └── lambda_function.py
│   └── get-available-slots/
│       └── lambda_function.py
├── docs/
│   └── architecture/
└── screenshots/
```

## Future Improvements

Potential next steps include adding authentication, an administrative appointment dashboard, automated infrastructure deployment with AWS SAM/Terraform/CloudFormation, CI/CD with GitHub Actions, automated tests, monitoring/alarms, a custom domain, and stronger production-grade security controls.

A production-scale DynamoDB design would also replace the availability scan with a query-oriented access pattern and appropriate keys/indexes.

## Project Status

**Core application: Completed and successfully tested.**

The project achieved its primary objectives: a serverless medical appointment application capable of retrieving availability, booking appointments, preventing duplicate bookings, persisting appointment data, sending email confirmations, and serving its frontend through AWS infrastructure.

---

Built as a hands-on AWS cloud/serverless engineering portfolio project.