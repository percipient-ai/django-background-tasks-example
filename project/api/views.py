from django.http import JsonResponse
from django.shortcuts import render
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.response import Response
from api.mq_client import RabbitMQClient
from logging import getLogger

from .tasks import demo_task

logger = getLogger(__name__)
RMQ = RabbitMQClient()

@csrf_exempt
def tasks(request):
    if request.method == 'POST':
        return _post_tasks(request)
    else:
        return JsonResponse({}, status=405)

class SearchQueue(APIView):
    def get(self, request):
        return Response(status=status.HTTP_200_OK)

    def post(self, request):
        q = request.data['query']
        RMQ.submit_search_job(q)
        return Response(status=status.HTTP_201_CREATED)

def _post_tasks(request):
    message = request.POST['message']
    logger.debug('calling demo_task. message={0}'.format(message))
    demo_task(message)
    return JsonResponse({}, status=302)
