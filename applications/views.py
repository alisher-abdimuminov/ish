from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import ApplicationForm
from .models import Application


@login_required
def home_view(request):
    try:
        app_instance = request.user.application
    except Application.DoesNotExist:
        app_instance = None

    if request.method == "POST":
        form = ApplicationForm(request.POST, request.FILES, instance=app_instance)
        if form.is_dict() if hasattr(form, "is_dict") else form.is_valid():
            app = form.save(commit=False)
            app.user = request.user
            app.save()
            messages.success(request, "Hujjatlaringiz muvaffaqiyatli saqlandi!")
            return redirect("home")
    else:
        form = ApplicationForm(instance=app_instance)

    return render(
        request, "applications/index.html", {"form": form, "app_instance": app_instance}
    )
