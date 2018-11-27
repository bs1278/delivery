"""
	Author : Bala
	Description : StoreManager and DeliveryTask models lives in this file
	Note : 
"""

import datetime
import logging
import traceback
from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext as _
from django.utils import timezone
from django.contrib.auth.models import User
from django.conf import settings
from django.dispatch import receiver
from django.urls import reverse
from django.core.validators import ValidationError
from django.db.models.signals import post_save
from rest_framework.authtoken.models import Token
from store.consts import validation_messages
# Create your models here.

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
	if created:
		Token.objects.create(user=instance)


class Store(models.Model):
	"""
		store manager model
	"""
	user = models.OneToOneField(User, 
								on_delete=models.CASCADE, 
								related_name='store')
	store_name = models.CharField(max_length=150)
	contact_number = models.CharField(max_length=12)

	def __str__(self):
		return self.store_name

	def __repr__(self):
		return self.store_name

	

	def validate_unique(self, *args, **kwargs):
		"""
			validates store_name and contact number as a unique
		"""
		super(Store, self).validate_unique(*args, **kwargs)
		sn_qs = self.__class__._default_manager.filter(
						store_name=self.store_name).exists()
		cn_qs = self.__class__._default_manager.filter(
						contact_number=self.contact_number).exists()
		if sn_qs:
			raise ValidationError(validation_messages.get("DUPLICATE_STORE"))
		if cn_qs:
			raise ValidationError(validation_messages.get("DUPLICATE_NUMBER"))

	def clean(self, *args, **kwargs):
		if self.store_name:
			self.store_name=self.store_name.lower()

	def save(self, *args, **kwargs):
		super(Store, self).save(*args, **kwargs)

	class Meta:
		verbose_name = _("Store Manager")
		verbose_name_plural = _("Store Managers")


class DeliveryBoy(models.Model):
	"""
		delivery boy model
	"""
	user = models.OneToOneField(User, 
								on_delete=models.CASCADE, 
								related_name='delivery_boy')
	number = models.CharField(max_length=12, unique=True)

	def __str__(self):
		return self.user.get_full_name()

	def __repr__(self):
		return self.user.get_full_name()

	def validate_unique(self, *args, **kwargs):
		super(DeliveryBoy, self).validate_unique(*args, **kwargs)
		#qs = self.__class__._default_manger.filter(number=self.number).exists()
		qs = DeliveryBoy.objects.filter(number=self.number).exists()
		if qs:
			raise ValidationError(validation_messages.get("DUPLICATE_NUMBER"))
	
	class Meta:
		verbose_name = _("Delivery Boy")
		verbose_name_plural = _("Delivery Boys")


class Task(models.Model):
	"""
		task model 
	"""
	HIGH = 'HIGH'
	MEDIUM = 'MEDIUM'
	LOW = 'LOW'

	ACCEPTED = 'ACCEPTED'
	COMPLETED = 'COMPLETED'
	REJECTED = 'REJECTED'
	READY = 'READY'
	CANCELD = 'CANCELD'
	PREIORITY_CHOICES = (
		(HIGH, 'High'),
		(MEDIUM, 'Medium'),
		(LOW, 'Low'),
	)

	STATUS_CHOICES = (
		(READY, 'Ready'),
		(ACCEPTED, 'Accepted'),
		(COMPLETED, 'Completed'),
		(REJECTED, 'Rejected'),
		(CANCELD, 'Canceld')
	)

	title = models.CharField(max_length=100)
	store = models.ForeignKey(Store, on_delete=models.CASCADE)
	delivery_boy = models.ForeignKey(DeliveryBoy, 
									on_delete=models.CASCADE, 
									blank=True, null=True)
	preiority = models.CharField(max_length=6, choices=PREIORITY_CHOICES)
	status = models.CharField(max_length=10, choices=STATUS_CHOICES)
	created_at = models.DateTimeField( auto_now=True)
	accepted_at = models.DateTimeField(blank=True, null=True)
	completed_at = models.DateTimeField(blank=True, null=True)
	edited_at = models.DateTimeField(auto_now_add=True)
	celery_id = models.CharField(max_length=200, null=True, blank=True)

	def __str__(self):
		return self.title

	def __repr__(self):
		return self.title
	
	def get_absolute_url(self):
		return reverse('task_details', args=[str(self.id)])
	
	class Meta:
		verbose_name = _("Delivery Task")
		verbose_name_plural = _("Delivery Tasks")
		ordering = ('created_at',)







