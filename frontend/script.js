const API_URL = "https://trxy56elf1.execute-api.eu-north-1.amazonaws.com";

const doctorSelect = document.getElementById("doctor");
const dateInput = document.getElementById("appointmentDate");
const timeSelect = document.getElementById("appointmentTime");

async function loadAvailableSlots() {
    const doctorId = doctorSelect.value;
    const date = dateInput.value;

    if (!doctorId || !date) {
        timeSelect.innerHTML = '<option value="">Select a date first</option>';
        return;
    }

    timeSelect.innerHTML = '<option value="">Loading...</option>';

    try {
        const response = await fetch(
            `${API_URL}/slots?date=${encodeURIComponent(date)}&doctorId=${encodeURIComponent(doctorId)}`
        );

        if (!response.ok) {
            throw new Error(`HTTP error: ${response.status}`);
        }

        const data = await response.json();

        timeSelect.innerHTML = '<option value="">Select a time</option>';

        if (!data.availableSlots || data.availableSlots.length === 0) {
            timeSelect.innerHTML = '<option value="">No available times</option>';
            return;
        }

        data.availableSlots.forEach(slot => {
            const option = document.createElement("option");
            option.value = slot;
            option.textContent = slot;
            timeSelect.appendChild(option);
        });

    } catch (error) {
        console.error("Error loading available slots:", error);
        timeSelect.innerHTML = '<option value="">Could not load times</option>';
    }
}

doctorSelect.addEventListener("change", loadAvailableSlots);
dateInput.addEventListener("change", loadAvailableSlots);

const form = document.querySelector("form");

form.addEventListener("submit", async function (event) {
    event.preventDefault();

    const patientName = document.getElementById("patientName").value;
    const patientEmail = document.getElementById("patientEmail").value;
    const doctorId = doctorSelect.value;
    const appointmentDate = dateInput.value;
    const appointmentTime = timeSelect.value;

    const appointmentData = {
        PatientName: patientName,
        PatientEmail: patientEmail,
        DoctorID: doctorId,
        AppointmentDate: appointmentDate,
        AppointmentTime: appointmentTime
    };

    try {
        const response = await fetch(`${API_URL}/appointment`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(appointmentData)
        });

        const data = await response.json();

        if (!response.ok) {
            if (response.status === 409) {
                throw new Error(
                    "This appointment time is no longer available. Please choose another time."
                );
            }

            throw new Error(data.message || "Could not book appointment.");
        }

        document.getElementById("message").textContent =
            data.message || "Appointment successfully booked!";

    } catch (error) {
        console.error("Booking error:", error);

        document.getElementById("message").textContent =
            error.message || "Could not book appointment.";
    }
});