from rest_framework import serializers
from store.models import Store, Task,DeliveryBoy



class StoreSerializer(serializers.ModelSerializer):

	class Meta:
		model = Store
		fields = ("id", "store_name", "contact_number")


class TaskStoreSerializer(serializers.ModelSerializer):
	class Meta:
		model = Store
		fields = ("id", "store_name", "contact_number")


class TaskDeliverBoySerializer(serializers.ModelSerializer):
	name = serializers.ReadOnlyField(source="user.get_full_name")

	class Meta:
		model = DeliveryBoy
		fields = ("id", "name", "number")

class TaskSerializer(serializers.ModelSerializer):

	delivery_boy = TaskDeliverBoySerializer()
	store = TaskStoreSerializer()
	status = serializers.ReadOnlyField(source="get_status_display")

	class Meta:
		model = Task
		fields = ("id", "title", "store", "delivery_boy", "status", "preiority")

