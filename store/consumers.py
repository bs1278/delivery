import json
import logging
from channels import Channel
from channels.sessions import channel_session
from delivery.celery import app
from store.models import Task
from store.tasks import deliver_task_accept_notification_

log = logging.getLogger(__name__)


@channel_session
def ws_connect(message):
	message.reply_channel.send({
			"text": json.dumps({
				"action": "reply_channel",
				"reply_channel": message.reply_channel.name,
			})
	})


@channel_session
def ws_receive(message):
	try:
		data = json.loads(message['text'])
	except ValueError:
		log.debug("websocket message is not json text=%s", message['text'])
		return

	if data:
		reply_channel = models.reply_channel.name
		if data['action'] == 'push_task_accepted_notification':
			push_task_accepted_notification(data, reply_channel)
		if data['action'] == ''


def push_task_accepted_notification(data, reply_channel):
	log.debug("Task Name:%s", data['task_title'])
	# save model to our data base
	task = Task(
		title=data['task_title'],
		status=Task.READY,
		store = data['task_store'],
		preiority=data['task_preiority'],
	)
	task.save()
	# fireup celery task 
	accept_task = deliver_task_accept_notification_.delay(task.id, reply_channel)
	# store celery task id for future ref
	task.celery_id = accept_task.id
	task.save()

	# info client about task
	Channel(reply_channel).send({
		"text": json.dumps({
			"action": "started",
			"task_id": task.id,
			"task_name": task.title,
			"task_status": task.status,

		})
	})