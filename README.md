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
- Prevention of double booking
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
| Amazon DynamoDB | Stores appointment/booking data and supports booking validation |
| Amazon SES | Sends appointment confirmation emails |
| AWS IAM | Controls permissions between services |
| Amazon CloudWatch | Supports logging and troubleshooting of serverless functions |

## Architecture

```text
Patient / Browser
       |
       v
Amazon CloudFront
       |
       v
Amazon S3 (HTML / CSS / JavaScript)
       |
       | API requests
       v
Amazon API Gateway
       |
       v
AWS Lambda
   |       |
   |       +----> Amazon SES ----> Confirmation Email
   |
   +------------> Amazon DynamoDB
                    |
                    +---- Appointment availability
                    +---- Booking records
                    +---- Double-booking protection
```

## Application Flow

1. The patient opens the application through the CloudFront-hosted frontend.
2. The browser loads the HTML, CSS, and JavaScript assets stored in S3.
3. The frontend requests available appointment slots through API Gateway.
4. API Gateway invokes the appropriate Lambda function.
5. Lambda reads the appointment data and returns available slots.
6. The patient chooses a slot and submits their booking information.
7. The booking Lambda validates that the requested slot is still available.
8. The appointment is stored only when the booking conditions succeed.
9. The booked slot is no longer available for another successful booking.
10. Amazon SES sends an appointment confirmation email.
11. The frontend displays the successful booking result to the patient.

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

The backend therefore does not rely only on what the browser displays as available. Availability is checked again when the booking request reaches the backend, and the database operation protects the appointment slot from being booked twice.

This is important because frontend availability can become stale between the moment a patient views a slot and the moment they submit a booking.

Testing confirmed that a successfully booked appointment could not subsequently be booked again as though it were still available.

## Email Confirmation

After a successful booking, the backend integrates with Amazon SES to send an email confirmation to the patient.

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

A simple read-then-write workflow can create race conditions. Booking protection therefore needed to exist at the backend/database layer rather than depending on frontend state alone.

### Email delivery

The booking workflow also had to integrate correctly with Amazon SES so that confirmation messages were sent only as part of a successful appointment flow.

### Frontend deployment

The frontend was prepared as static HTML, CSS, and JavaScript files and uploaded to S3. CloudFront was then configured with S3 as its origin, private bucket access enabled, recommended origin/cache settings, and `index.html` as the default root object.

## Testing and Results

End-to-end testing verified the core requirements:

- The deployed frontend loaded successfully.
- Available appointment slots were retrieved.
- A patient could submit a valid appointment.
- Successful appointments were persisted.
- A previously booked slot could not be booked again successfully.
- A confirmation email was received after a successful booking.
- The frontend was successfully deployed through Amazon S3 and CloudFront.

## What I Learned

This project provided practical experience with designing and troubleshooting a multi-service AWS serverless application. Key lessons included:

- Designing serverless application flows
- Integrating API Gateway with Lambda
- Working with DynamoDB for application state
- Protecting data integrity during concurrent requests
- Configuring IAM permissions between AWS services
- Troubleshooting CORS between a browser frontend and an API
- Integrating transactional email with Amazon SES
- Hosting static applications in S3
- Using CloudFront with a private S3 origin
- Testing an application as a complete end-to-end system

## Security Considerations

The project keeps infrastructure exposure limited where possible. The S3 frontend origin is accessed through CloudFront instead of requiring the bucket to be generally public. IAM permissions should follow least-privilege principles, and AWS credentials or secrets must never be committed to this repository.

For a production medical system, additional controls would be required before storing or processing real patient health information, including appropriate authentication, authorization, encryption, auditing, data-retention policies, regulatory/compliance review, and operational monitoring.

## Repository Structure

The repository will be expanded as the project source is documented:

```text
aws-serverless-medical-appointment-system/
├── README.md
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── script.js
├── lambda/
│   ├── get-available-slots/
│   └── book-appointment/
├── docs/
│   └── architecture/
└── screenshots/
```

## Future Improvements

Potential next steps include adding authentication, an administrative appointment dashboard, automated infrastructure deployment with AWS SAM/Terraform/CloudFormation, CI/CD with GitHub Actions, automated tests, monitoring/alarms, a custom domain, and stronger production-grade security controls.

## Project Status

**Core application: Completed and successfully tested.**

The project achieved its primary objectives: a serverless medical appointment application capable of retrieving availability, booking appointments, preventing duplicate bookings, persisting appointment data, sending email confirmations, and serving its frontend through AWS infrastructure.

---

Built as a hands-on AWS cloud/serverless engineering portfolio project.