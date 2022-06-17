from email import message
from re import sub
from rest_framework.views import APIView
from django.core.mail import send_mail
from django.http import HttpResponse


def send_feedback_mail(feedback, current_url, user):
    message = (
        f"url: {current_url} "
        f"user: {user} "
        f"comments: {feedback}"
    )

    send_mail(
        'Feedback Zoekportaal Openleermaterialen',
        message,
        'noreply@edusources.nl',
        ['edusources-team@surf.nl']
    )

def send_contact_mail(subject, name, email, message, current_url):
    content = (
        f"name: {name} "
        f"email: {email} "
        f"message: {message} "
        f"url: {current_url} "
    )

    send_mail(
        f'{subject} Zoekportaal Openleermaterialen',
        content,
        email,
        ['edusources-team@surf.nl']
    )

class FeedbackAPIView(APIView):

    def post(self, request, *args, **kwargs):
        feedback = request.data["feedback"]
        current_url = request.data["current_url"]
        user = request.user
        send_feedback_mail(feedback, current_url, user)
        return HttpResponse(status=204)


class ContactAPIView(APIView):

    def post(self, request, *args, **kwargs):
        name = request.data["name"]
        subject = request.data["subject"]
        email = request.data["email"]
        message = request.data["message"]
        current_url = request.data["current_url"]
        send_contact_mail(subject, name, email, message, current_url)
        return HttpResponse(status=204)