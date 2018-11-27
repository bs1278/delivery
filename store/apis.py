import json

import datetime
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from oauth2_provider.models import AccessToken
from rest_framework import status
from store.models import Task, Store, DeliveryBoy
from store.serializers import (StoreSerializer, 
								TaskStoreSerializer, 
								TaskDeliverBoySerializer, 
								TaskSerializer)
# from store.tasks import (deliver_task_accept_notification,
# 						deliver_task_reject_notification,
# 						deliver_task_completed_notification, 
# 						store_created_new_task_notification)


###############
#   store     #
###############

def store_task_notification(request, last_request_time):
	notification = Task.objects.get(created_at__gt=last_request_time, status=Task.READY)
	return JsonResponse({"notification": notification})

def store_manager_cancel_task(request):
	"""
		end point for store manager can cancel task which is no longer accepted
	"""
	with transaction.atomic():
		# using atomic transations may be store manager and deliver boy
		# performs certain action at same time
		try:
			task_id = request.GET.get('task_id', None)
			task_instance = Task.objects.get(id=task_id, 
											store=request.user.store, 
											delivery_boy=None, 
											status=Task.READY)
			task_instance.status = Task.CANCELD
			task_instance.save()
			success_data = {
				'result': 'OK'
			}
			return JsonResponse(success_data, 
								status=status.HTTP_200_OK)
		except ValueError:
			return JsonResponse(
					{"status": "failed", 
					"error":"task accepted by delivery boy"})	

def get_store_manager_all_tasks(request):
	"""
		end point for store manager to retrive all tasks
	"""
	tasks = TaskSerializer(
		Task.objects.filter(store=request.user.store).order_by("-id"),
		many=True
		).data
	return JsonResponse({"tasks" : tasks})



def delivery_boy_accept_task(request):
	"""
		end point for deliver boy can accpet task
	"""
	task_id = request.GET.get('task_id', None)
	if Task.objects.filter(delivery_boy=request.user.delivery_boy, status=Task.ACCEPTED).count() >= 3:
		return JsonResponse({"status": "failed", "error": "reaced maximum limit"})

	with transaction.atomic():
		# using atomic transactions to avoid race conditions
		# may two users can access same resource at a time to avoid that 
		try:
			task_instance = Task.objects.get(id=task_id, delivery_boy=None)
			task_instance.status = Task.ACCEPTED
			task_instance.delivery_boy = request.user.delivery_boy
			task_instance.accepted_at = datetime.datetime.now()
			task_instance.save()
			success_data = {
				"result": "success"
			}
			# delivery_boy_accept_task.delay(task_instance.id)
			return JsonResponse(success_data, status=status.HTTP_201_CREATED)

		except Task.DoesNotExist:
				return JsonResponse({"status": "failed", "error":"task accepted by another delivery boy"})


def delivery_boy_reject_task(request):
	"""
		endpoint for deliver boy for rejecting task
	"""
	task_id = request.GET.get('task_id', None)
	d_boy = request.user.delivery_boy
	task = Task.objects.get(id=task_id, 
							delivery_boy=d_boy, 
							status=Task.ACCEPTED)
	task.status = Task.READY
	task.delivery_boy = None
	task_id = task.id
	task.save()
	# delivery_boy_reject_task.delay(task_id)
	return JsonResponse({"status": "success"}, status=status.HTTP_200_OK)


def delivery_boy_complete_task(request):
	"""
		end point for deliver boy for completed task
	"""
	task_id = request.GET.get('task_id', None)
	d_boy = request.user.delivery_boy
	task = Task.objects.get(id=task_id, delivery_boy=d_boy)
	task.status = Task.COMPLETED
	task_id = task.id
	task.save()
	# deliver_task_completed_notification.delay(task_id)
	return JsonResponse({"status": "success"}, status=status.HTTP_200_OK)


def get_deliver_boy_completed_tasks(request):
	access_token = AccessToken.objects.get(
		token = request.GET.get("access_token"),
        expires__gt = timezone.now())
	d_boy = access_token.user.delivery_boy	
	tasks = TaskSerializer(
		Task.objects.filter(status=Task.COMPLETED, delivery_boy=d_boy).order_by("-id"),
		many=True
		).data
	return JsonResponse({"tasks" : tasks})


def delivery_boy_ready_new_tasks(request):
	tasks = TaskSerializer(
		Task.objects.filter(status=Task.READY, delivery_boy=None).order_by("-id"),
		many=True
		).data
	return JsonResponse({"tasks" : tasks})


def delivery_boy_get_latest_task(request):
	access_token = AccessToken.objects.get(token=request.GET.get("access_token"), expires__gt=timezone.now())
	d_boy = access_token.user.delivery_boy
	tasks = TaskSerializer(Task.objects.get.filter(delivery_boy=d_boy).order_by("-created_at").last()).data
	return JsonResponse({"task": task})



#######################
#	token end points  #
#######################

@csrf_exempt
def delivery_boy_accept_task_token(request):
	if request.method == 'POST':
		access_token = AccessToken.objects.get(token=request.POST.get("access_token"), expires__gt=timezone.now())
		d_boy = access_token.user.delivery_boy
		
		if Task.objects.filter(delivery_boy=d_boy).exclude(status=Task.ACCEPTED):
			return JsonResponse({"status": "failed", "error": "You can accept one task at a time"})

		with transaction.atomic():
			try:
				task = Task.objects.select_for_update().get(
					id=request.POST["task_id"],
					delivery_boy=None)
				task.delivery_boy = d_boy
				task.status = Task.ACCEPTED
				# implement push notification here store manager
				task.save()
				return JsonResponse({"status": "success"})

			except Task.DoesNotExist:
				return JsonResponse({"status": "failed", "error":"task accepted by another delivery boy"})


def delivery_boy_complete_task_token(request):
	access_token = AccessToken.objects.get(token=request.POST.get("access_token"), expires__gt=timezone.now())
	d_boy = access_token.user.delivery_boy
	task = Task.objects.get(id=request.POST["task_id"], delivery_boy=d_boy)
	task.status = Task.COMPLETED
	# implement push notification here store manager
	task.save()
	return JsonResponse({"status": "success"})


def delivery_boy_reject_task_token(request):
	access_token = AccessToken.objects.get(token=request.POST.get("access_token"), expires__gt=timezone.now())
	d_boy = access_token.user.delivery_boy
	task = Task.objects.get(id=request.POST["task_id"], delivery_boy=d_boy, status=Task.ACCEPTED)
	task.status = Task.READY
	# implement push notification here store manager
	task.save()
	return JsonResponse({"status": "success"})