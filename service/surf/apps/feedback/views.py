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


class FeedbackAPIView(APIView):
    def post(self, request, *args, **kwargs):
        feedback = request.data["feedback"]
        current_url = request.data["current_url"]
        user = request.user
        send_feedback_mail(feedback, current_url, user)
        return HttpResponse(status=204)
