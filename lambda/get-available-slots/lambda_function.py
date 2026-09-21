import json
import boto3
from datetime import datetime

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("MedicalAppointment")

# Clinic appointment schedule
ALL_SLOTS = [
    "09:00",
    "09:30",
    "10:00",
    "10:30",
    "11:00",
    "11:30",
    "14:00",
    "14:30",
    "15:00",
    "15:30",
    "16:00",
    "16:30"
]


def lambda_handler(event, context):

    try:
        # API Gateway request:
        # GET /slots?date=2026-10-22&doctorId=DOCTOR001
        params = event.get("queryStringParameters") or {}

        appointment_date = params.get("date")
        doctor_id = params.get("doctorId", "DOCTOR001")

        if not appointment_date:
            return response(400, {
                "success": False,
                "message": "Please provide an appointment date."
            })

        # Validate date format
        try:
            selected_date = datetime.strptime(
                appointment_date, "%Y-%m-%d"
            ).date()
        except ValueError:
            return response(400, {
                "success": False,
                "message": "Date must use YYYY-MM-DD format."
            })

        # Monday = 0, Sunday = 6
        if selected_date.weekday() >= 5:
            return response(400, {
                "success": False,
                "message": "Appointments are not available on weekends."
            })

        # Find appointments already booked for this doctor/date
        result = table.scan(
            ProjectionExpression="SlotID"
        )

        booked_slots = set()

        prefix = f"{doctor_id}#{appointment_date}#"

        for item in result.get("Items", []):
            slot_id = item.get("SlotID", "")

            if slot_id.startswith(prefix):
                booked_time = slot_id.split("#")[-1]
                booked_slots.add(booked_time)

        # Remove booked times
        available_slots = [
            slot for slot in ALL_SLOTS
            if slot not in booked_slots
        ]

        return response(200, {
            "success": True,
            "doctorId": doctor_id,
            "date": appointment_date,
            "availableSlots": available_slots
        })

    except Exception as error:
        print("ERROR:", str(error))

        return response(500, {
            "success": False,
            "message": "Unable to retrieve available appointments."
        })


def response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET,OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type"
        },
        "body": json.dumps(body)
    }
