from django.conf import settings
from django.db import models


class Application(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Kutilmoqda"
        APPROVED = "approved", "Tasdiqlandi"
        REJECTED = "rejected", "Rad etildi"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="application",
    )

    rector_application = models.FileField(
        upload_to="docs/rector/",
        verbose_name="Institut rektori nomiga ariza",
        null=True,
        blank=True,
    )
    rector_application_status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    rector_application_comment = models.TextField(
        null=True,
        blank=True,
    )

    passport = models.FileField(
        upload_to="docs/passport/",
        verbose_name="Pasport yoki ID-shaxs guvohnomasi nusxasi",
        null=True,
        blank=True,
    )
    passport_status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    passport_comment = models.TextField(
        null=True,
        blank=True,
    )

    diploma = models.FileField(
        upload_to="docs/diploma/",
        verbose_name="Oliy ma'lumot, ilmiy daraja to'g'risidagi diplomlar nusxasi",
        null=True,
        blank=True,
    )
    diploma_status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    diploma_comment = models.TextField(
        null=True,
        blank=True,
    )

    m_diploma = models.FileField(
        upload_to="docs/m_diploma/",
        verbose_name="Magistr to'g'risidagi diplomlar nusxasi",
        null=True,
        blank=True,
    )
    m_diploma_status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    m_diploma_comment = models.TextField(
        null=True,
        blank=True,
    )

    degree_diploma = models.FileField(
        upload_to="docs/degree/",
        verbose_name="Ilmiy unvoni to'g'risidagi diplomlar nusxasi",
        null=True,
        blank=True,
    )
    degree_diploma_status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    degree_diploma_comment = models.TextField(
        null=True,
        blank=True,
    )

    resume = models.FileField(
        upload_to="docs/resume/",
        verbose_name="Rezyume-ma'lumotnoma",
        null=True,
        blank=True,
    )
    resume_status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    resume_comment = models.TextField(
        null=True,
        blank=True,
    )

    qualification_cert = models.FileField(
        upload_to="docs/qualification/",
        blank=True,
        null=True,
        verbose_name="Malaka oshirganligi to'g'risidagi guvohnoma",
    )
    qualification_cert_status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    qualification_cert_comment = models.TextField(
        null=True,
        blank=True,
    )

    scientific_works = models.FileField(
        upload_to="docs/works/",
        blank=True,
        null=True,
        verbose_name="Ilmiy ishlar ro'yxati",
    )
    scientific_works_status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    scientific_works_comment = models.TextField(
        null=True,
        blank=True,
    )

    language_cert = models.FileField(
        upload_to="docs/languages/",
        blank=True,
        null=True,
        verbose_name="Xorijiy tillarni bilish darajasini belgilovchi sertifikatlar",
    )
    language_cert_status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    language_cert_comment = models.TextField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Ariza: {self.user.get_full_name()}"
