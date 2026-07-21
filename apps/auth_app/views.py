from django.views.generic import TemplateView


class ProfileView(TemplateView):
    template_name = "auth/profile.html"


class DriverView(TemplateView):
    template_name = "driver/driver.html"
