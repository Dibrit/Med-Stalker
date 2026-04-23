import random
import string
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
from faker import Faker

from api.models import Appointment, Diagnosis, DoctorProfile, PatientProfile, Prescription


User = get_user_model()


def _rand_digits(rng: random.Random, n: int) -> str:
    return "".join(rng.choice(string.digits) for _ in range(n))


def _rand_upper_alnum(rng: random.Random, n: int) -> str:
    alphabet = string.ascii_uppercase + string.digits
    return "".join(rng.choice(alphabet) for _ in range(n))


def _pick(rng: random.Random, items: list[str]) -> str:
    return items[rng.randrange(0, len(items))]


SPECIALIZATIONS = [
    "Family Medicine",
    "Internal Medicine",
    "Pediatrics",
    "Cardiology",
    "Neurology",
    "Dermatology",
    "Psychiatry",
    "Orthopedics",
    "Endocrinology",
    "Pulmonology",
]

CONDITIONS = [
    ("Hypertension", "I10"),
    ("Type 2 diabetes mellitus", "E11.9"),
    ("Acute bronchitis", "J20.9"),
    ("Migraine", "G43.909"),
    ("Generalized anxiety disorder", "F41.1"),
    ("Major depressive disorder", "F32.9"),
    ("Hyperlipidemia", "E78.5"),
    ("Asthma", "J45.909"),
    ("Gastroesophageal reflux disease", "K21.9"),
    ("Low back pain", "M54.50"),
    ("Allergic rhinitis", "J30.9"),
]

MEDICATIONS = [
    "Amoxicillin",
    "Azithromycin",
    "Metformin",
    "Lisinopril",
    "Amlodipine",
    "Atorvastatin",
    "Omeprazole",
    "Albuterol inhaler",
    "Sertraline",
    "Ibuprofen",
    "Acetaminophen",
]

INSTRUCTIONS = [
    "Take 1 tablet by mouth once daily with food.",
    "Take 1 tablet by mouth twice daily.",
    "Take 1 capsule by mouth every 8 hours for 5 days.",
    "Use 2 puffs every 4–6 hours as needed for wheezing.",
    "Avoid alcohol; maintain adequate hydration.",
    "Increase physical activity as tolerated; follow a low-sodium diet.",
    "Monitor blood pressure at home and record daily readings.",
    "Return for follow-up in 2 weeks or sooner if symptoms worsen.",
]

APPOINTMENT_REASONS = [
    "Routine follow-up visit.",
    "Persistent cough and sore throat.",
    "Medication review and refill discussion.",
    "Blood pressure check after home monitoring.",
    "Migraine symptoms getting worse.",
    "General wellness consultation.",
    "Skin rash that has not improved.",
]


class Command(BaseCommand):
    help = "Seed the local dev database with realistic-looking demo data."

    def add_arguments(self, parser):
        parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducible data.")
        parser.add_argument("--doctors", type=int, default=5, help="Number of doctors to create.")
        parser.add_argument("--patients", type=int, default=30, help="Number of patients to create.")
        parser.add_argument("--diagnoses", type=int, default=120, help="Number of diagnoses to create.")
        parser.add_argument("--prescriptions", type=int, default=120, help="Number of prescriptions to create.")
        parser.add_argument("--appointments", type=int, default=80, help="Number of appointments to create.")
        parser.add_argument(
            "--password",
            type=str,
            default="secret123",
            help="Password set for all created users (dev only).",
        )
        parser.add_argument(
            "--prefix",
            type=str,
            default="demo",
            help="Username prefix for created accounts (idempotent by prefix).",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        seed = int(options["seed"])
        rng = random.Random(seed)
        fake = Faker()
        Faker.seed(seed)

        prefix: str = options["prefix"]
        password: str = options["password"]
        n_doctors: int = max(0, int(options["doctors"]))
        n_patients: int = max(0, int(options["patients"]))
        n_diagnoses: int = max(0, int(options["diagnoses"]))
        n_prescriptions: int = max(0, int(options["prescriptions"]))
        n_appointments: int = max(0, int(options["appointments"]))

        doctors = self._ensure_doctors(fake=fake, rng=rng, prefix=prefix, password=password, n=n_doctors)
        patients = self._ensure_patients(fake=fake, rng=rng, prefix=prefix, password=password, n=n_patients)

        if doctors and patients and n_diagnoses:
            self._create_diagnoses(fake=fake, rng=rng, doctors=doctors, patients=patients, n=n_diagnoses)
        if doctors and patients and n_prescriptions:
            self._create_prescriptions(rng=rng, doctors=doctors, patients=patients, n=n_prescriptions)
        if doctors and patients and n_appointments:
            self._create_appointments(rng=rng, doctors=doctors, patients=patients, n=n_appointments)

        self.stdout.write(
            self.style.SUCCESS(
                f"Seed complete. Doctors={len(doctors)} Patients={len(patients)} "
                f"(seed={seed}, prefix={prefix!r})."
            )
        )

    def _ensure_doctors(self, *, fake: Faker, rng: random.Random, prefix: str, password: str, n: int):
        doctors: list[DoctorProfile] = []
        for i in range(1, n + 1):
            username = f"{prefix}_doctor_{i:03d}"
            first_name = fake.first_name()
            last_name = fake.last_name()
            email = f"{username}@example.test"

            user, created = User.objects.get_or_create(
                username=username,
                defaults={"first_name": first_name, "last_name": last_name, "email": email},
            )
            if created:
                user.set_password(password)
                user.save(update_fields=["password"])

            profile, _ = DoctorProfile.objects.get_or_create(
                user=user,
                defaults={
                    "specialization": _pick(rng, SPECIALIZATIONS),
                    "license_number": f"LIC-{_rand_upper_alnum(rng, 8)}",
                },
            )
            doctors.append(profile)

        self.stdout.write(f"Doctors ready: {len(doctors)}")
        return doctors

    def _ensure_patients(self, *, fake: Faker, rng: random.Random, prefix: str, password: str, n: int):
        patients: list[PatientProfile] = []
        now = timezone.now()
        for i in range(1, n + 1):
            username = f"{prefix}_patient_{i:03d}"
            first_name = fake.first_name()
            last_name = fake.last_name()
            email = f"{username}@example.test"

            user, created = User.objects.get_or_create(
                username=username,
                defaults={"first_name": first_name, "last_name": last_name, "email": email},
            )
            if created:
                user.set_password(password)
                user.save(update_fields=["password"])

            # Age 1..95 years
            age_years = rng.randint(1, 95)
            dob = (now.date() - timedelta(days=age_years * 365 + rng.randint(0, 364)))

            mrn_default = f"MRN-{prefix.upper()}-{_rand_digits(rng, 8)}"
            phone_default = fake.phone_number()

            profile, _ = PatientProfile.objects.get_or_create(
                user=user,
                defaults={
                    "date_of_birth": dob,
                    "phone": phone_default,
                    "medical_record_number": self._unique_mrn(rng=rng, base=mrn_default),
                },
            )
            patients.append(profile)

        self.stdout.write(f"Patients ready: {len(patients)}")
        return patients

    def _unique_mrn(self, *, rng: random.Random, base: str) -> str:
        mrn = base
        # SQLite + unique constraint: avoid collisions if random repeats.
        for _ in range(20):
            if not PatientProfile.objects.filter(medical_record_number=mrn).exists():
                return mrn
            mrn = f"{base}-{_rand_digits(rng, 3)}"
        return f"{base}-{timezone.now().strftime('%H%M%S')}"

    def _create_diagnoses(
        self,
        *,
        fake: Faker,
        rng: random.Random,
        doctors: list[DoctorProfile],
        patients: list[PatientProfile],
        n: int,
    ):
        statuses = [Diagnosis.Status.ACTIVE, Diagnosis.Status.RESOLVED, Diagnosis.Status.CHRONIC]
        now = timezone.now()

        created = 0
        for _ in range(n):
            doctor = doctors[rng.randrange(0, len(doctors))]
            patient = patients[rng.randrange(0, len(patients))]
            title, icd = CONDITIONS[rng.randrange(0, len(CONDITIONS))]

            diagnosed_at = now - timedelta(days=rng.randint(0, 365 * 3), hours=rng.randint(0, 23))
            status = statuses[rng.randrange(0, len(statuses))]

            # Keep it "real-looking" but not too long.
            description = "\n".join(
                [
                    fake.sentence(nb_words=rng.randint(8, 14)),
                    fake.sentence(nb_words=rng.randint(8, 14)),
                ]
            )

            Diagnosis.objects.create(
                patient=patient,
                recorded_by=doctor,
                title=title,
                description=description,
                icd_code=icd,
                status=status,
                diagnosed_at=diagnosed_at,
            )
            created += 1

        self.stdout.write(f"Diagnoses created: {created}")

    def _create_prescriptions(
        self,
        *,
        rng: random.Random,
        doctors: list[DoctorProfile],
        patients: list[PatientProfile],
        n: int,
    ):
        now = timezone.now()

        created = 0
        for _ in range(n):
            doctor = doctors[rng.randrange(0, len(doctors))]
            patient = patients[rng.randrange(0, len(patients))]

            # Optionally tie to one of the patient's diagnoses
            dx_qs = patient.diagnoses.all()
            diagnosis = dx_qs.order_by("?").first() if dx_qs.exists() and rng.random() < 0.7 else None

            issued_at = now - timedelta(days=rng.randint(0, 365 * 2), hours=rng.randint(0, 23))
            valid_until = (issued_at.date() + timedelta(days=rng.choice([7, 14, 30, 90]))) if rng.random() < 0.6 else None

            medication_name = _pick(rng, MEDICATIONS) if rng.random() < 0.85 else ""
            instructions = _pick(rng, INSTRUCTIONS)

            Prescription.objects.create(
                patient=patient,
                prescribed_by=doctor,
                diagnosis=diagnosis,
                medication_name=medication_name,
                instructions=instructions,
                issued_at=issued_at,
                valid_until=valid_until,
            )
            created += 1

        self.stdout.write(f"Prescriptions created: {created}")

    def _create_appointments(
        self,
        *,
        rng: random.Random,
        doctors: list[DoctorProfile],
        patients: list[PatientProfile],
        n: int,
    ):
        now = timezone.now()
        statuses = [
            Appointment.Status.REQUESTED,
            Appointment.Status.CONFIRMED,
            Appointment.Status.CANCELLED,
            Appointment.Status.COMPLETED,
        ]

        created = 0
        attempts = 0
        max_attempts = max(n * 20, 20)

        while created < n and attempts < max_attempts:
            attempts += 1
            doctor = doctors[rng.randrange(0, len(doctors))]
            patient = patients[rng.randrange(0, len(patients))]
            status = statuses[rng.randrange(0, len(statuses))]

            if status == Appointment.Status.COMPLETED:
                day_offset = -rng.randint(1, 180)
            elif status == Appointment.Status.CANCELLED and rng.random() < 0.5:
                day_offset = -rng.randint(1, 60)
            else:
                day_offset = rng.randint(1, 90)

            starts_at = (now + timedelta(days=day_offset)).replace(
                hour=rng.randint(8, 17),
                minute=rng.choice([0, 30]),
                second=0,
                microsecond=0,
            )
            try:
                Appointment.objects.create(
                    patient=patient,
                    doctor=doctor,
                    status=status,
                    reason=_pick(rng, APPOINTMENT_REASONS),
                    starts_at=starts_at,
                )
            except ValidationError:
                continue

            created += 1

        self.stdout.write(f"Appointments created: {created}")
