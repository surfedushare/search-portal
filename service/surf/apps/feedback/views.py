from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django.core.mail import send_mail
from django.http import HttpResponse


def send_feedback_mail(feedback, current_url, user):
    print(feedback, current_url, user)

    res = send_mail(
        'Feedback Zoekportaal Openleermaterialen',
        feedback,
        'noreply@edusources.nl',
        ['kirsten.ruys@gmail.com']
    )

    return HttpResponse('%s' % res)


class FeedbackAPIView(APIView):
    def post(self, request, *args, **kwargs):
        feedback = request.data["feedback"]
        current_url = request.data["current_url"]
        user = request.user
        res = send_feedback_mail(feedback, current_url, user)
        return Response(status=res)
