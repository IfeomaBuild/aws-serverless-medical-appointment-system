import json
import boto3
import uuid
import os
from botocore.exceptions import ClientError

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("MedicalAppointment")
ses = boto3.client("ses", region_name="eu-north-1")

SES_FROM_EMAIL = os.environ.get("SES_FROM_EMAIL")


def lambda_handler(event, context):

    try:
        # API Gateway sends patient data inside "body".
        # Direct Lambda tests send the data directly.
        if "body" in event:
            if isinstance(event["body"], str):
                data = json.loads(event["body"])
            else:
                data = event["body"]
        else:
            data = event

        patient_name = data["PatientName"]
        patient_email = data["PatientEmail"]
        doctor_id = data["DoctorID"]
        appointment_date = data["AppointmentDate"]
        appointment_time = data["AppointmentTime"]

        # Unique doctor/date/time combination
        slot_id = f"{doctor_id}#{appointment_date}#{appointment_time}"

        appointment_id = "APT-" + str(uuid.uuid4())[:8].upper()

        # Atomic conditional write prevents double booking
        table.put_item(
            Item={
                "SlotID": slot_id,
                "AppointmentID": appointment_id,
                "PatientName": patient_name,
                "PatientEmail": patient_email,
                "DoctorID": doctor_id,
                "AppointmentDate": appointment_date,
                "AppointmentTime": appointment_time,
                "Status": "CONFIRMED"
            },
            ConditionExpression="attribute_not_exists(SlotID)"
        )

        if not SES_FROM_EMAIL:
            raise ValueError("SES_FROM_EMAIL environment variable is not configured.")

        ses.send_email(
            Source=SES_FROM_EMAIL,
            Destination={
                "ToAddresses": [patient_email]
            },
            Message={
                "Subject": {
                    "Data": "Medical Appointment Confirmation"
                },
                "Body": {
                    "Text": {
                        "Data": (
                            f"Hello {patient_name},\n\n"
                            f"Your medical appointment has been successfully booked.\n\n"
                            f"Appointment ID: {appointment_id}\n"
                            f"Doctor: {doctor_id}\n"
                            f"Date: {appointment_date}\n"
                            f"Time: {appointment_time}\n\n"
                            f"Thank you."
                        )
                    }
                }
            }
        )

        return {
            "statusCode": 201,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps({
                "success": True,
                "message": "Appointment successfully booked",
                "appointmentId": appointment_id,
                "date": appointment_date,
                "time": appointment_time
            })
        }

    except ClientError as error:

        if error.response["Error"]["Code"] == "ConditionalCheckFailedException":
            return {
                "statusCode": 409,
                "headers": {
                    "Content-Type": "application/json"
                },
                "body": json.dumps({
                    "success": False,
                    "message": "This appointment slot is already booked."
                })
            }

        raise error

    except (KeyError, json.JSONDecodeError) as error:
        return {
            "statusCode": 400,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps({
                "success": False,
                "message": "Invalid appointment request.",
                "error": str(error)
            })
        }
