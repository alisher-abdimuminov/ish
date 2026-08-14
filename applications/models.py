from django.conf import settings
from django.db import models


class Application(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="application"
    )

    rector_application = models.FileField(
        upload_to="docs/rector/",
        verbose_name="Institut rektori nomiga ariza",
        null=True,
        blank=True,
    )
    passport = models.FileField(
        upload_to="docs/passport/",
        verbose_name="Pasport yoki ID-shaxs guvohnomasi nusxasi",
        null=True,
        blank=True,
    )
    diploma = models.FileField(
        upload_to="docs/diploma/",
        verbose_name="Oliy ma'lumot, ilmiy daraja to'g'risidagi diplomlar nusxasi",
        null=True,
        blank=True,
    )
    degree_diploma = models.FileField(
        upload_to="docs/degree/",
        verbose_name="Ilmiy unvoni to'g'risidagi diplomlar nusxasi",
        null=True,
        blank=True,
    )
    resume = models.FileField(
        upload_to="docs/resume/",
        verbose_name="Rezyume-ma'lumotnoma",
        null=True,
        blank=True,
    )

    qualification_cert = models.FileField(
        upload_to="docs/qualification/",
        blank=True,
        null=True,
        verbose_name="Malaka oshirganligi to'g'risidagi guvohnoma",
    )
    scientific_works = models.FileField(
        upload_to="docs/works/",
        blank=True,
        null=True,
        verbose_name="Ilmiy ishlar ro'yxati",
    )
    language_cert = models.FileField(
        upload_to="docs/languages/",
        blank=True,
        null=True,
        verbose_name="Xorijiy tillarni bilish darajasini belgilovchi sertifikatlar",
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name="Ariza holati",
    )

    rejection_comment = models.TextField(
        null=True,
        blank=True,
        verbose_name="Rad etish sababi",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Ariza: {self.user.get_full_name()}"
