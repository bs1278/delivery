from __future__ import absolute_import
import time
import json
import logging
from django.http import JsonResponse
from django.http.response import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.contrib.auth.models import User
from channels import Channel
from celery import shared_task
from celery.utils.log import get_task_logger
from store.models import Store, Task, DeliveryBoy
from store.serializers import TaskSerializer
from delivery.celery import app


log = logging.getLogger(__name__)
logger = get_task_logger(__name__)


@app.task
def deliver_task_accept_notification(task_id, reply_channel):
	task = Task.objects.get(pk=task_id)
	log.debug("Running Task_name=%s", task.title)
	task.status = Task.ACCEPTED
	task.save()

	# send status update back to browser client

	if reply_channel is not None:
		Channel(replay_channel).send({
			"text": json.dumps({
					"action": "deliver_task_accept_notification",
					"task_id": task_id,
					"task_name": task.title,
					"task_status": task.status,
					"task_preiority": task.preiority,
					"task_store": task.store,
				})
			})


@app.task
def store_manager_created_new_task(task_id, reply_channel):
	task = Task.objects.get(pk=task_id)
	log.debug("Running Task Name=%s", task.title)
	if reply_channel is not None:
		Channel(reply_channel).send({
				"text": json.dumps({
					"action": "task_created",
					"task_id": task_id,
					"task_title": task.title,
					"task_status": task.status,
					"task_preiority": task.preiority,
					"task_store": task.store
				})
			})


@app.task
def deliver_task_reject_notification(task_id, reply_channel):
	task = Task.objects.get(pk=task_id)
	log.debug("Running Task Name=%s", task.title)
	if reply_channel is not None:
		Channel(reply_channel).send({
				"text": json.dumps({
					"action": "accepted",
					"task_id": task_id,
					"task_name": task.title,
					"task_status": task.status,
					"task_preiority": task.preiority,
					"task_store": task.store,
				})
			})


@app.task
def deliver_task_completed_notification(task_id, reply_channel):
	task = Task.objects.get(pk=task_id)
	log.debug("Running Task Name=%s", task.title)
	if reply_channel is not None:
		Channel(reply_channel).send({
				"text": json.dumps({
					"action": "accepted",
					"task_id": task_id,
					"task_name": task.title,
					"task_status": task.status,
					"task_preiority": task.preiority,
					"task_store": task.store,
				})
		})	