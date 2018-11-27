from django import forms
from django.utils.translation import ugettext as _
from django.core.validators import ValidationError
from django.contrib.auth.models import User
from store.models import Task, Store, DeliveryBoy



class UserForm(forms.ModelForm):
	"""
		Simple Django authentication User form for signup
	"""

	email = forms.EmailField(max_length=150, required=True)
	password = forms.CharField(widget=forms.PasswordInput())

	class Meta:
		model = User
		fields = ("username", "password", "first_name", "last_name", "email")

	def __init__(self, *args, **kwargs):
		super(UserForm, self).__init__(*args, **kwargs)
		self.fields['username'].widget.attrs.update({'class': 'form-control'})
		self.fields['password'].widget.attrs.update({'class': 'form-control'})
		self.fields['first_name'].widget.attrs.update({'class': 'form-control'})
		self.fields['last_name'].widget.attrs.update({'class': 'form-control'})
		self.fields['email'].widget.attrs.update({'class': 'form-control'})


class UserEditForm(forms.ModelForm):
	"""
		user edit form for profile section
	"""
	email = forms.EmailField(max_length=150, required=True)

	class Meta:
		model = User
		fields = ("first_name", "last_name", "email")

	def __init__(self, *args, **kwargs):
		super(UserEditForm, self).__init__(*args, **kwargs)
		self.fields['first_name'].widget.attrs.update({'class': 'form-control'})
		self.fields['last_name'].widget.attrs.update({'class': 'form-control'})
		self.fields['email'].widget.attrs.update({'class': 'form-control'})


class StoreForm(forms.ModelForm):
	"""
		store form for store managers
	"""
	validation_messages = {
		"duplicate_store": "Store Name Already exists" ,
		"dupicate_number": "Number Already exists with Store"
	}

	class Meta:
		model = Store
		fields = ('store_name', 'contact_number')

		labels = {
			'store_name': "Enter Store Name",
			'contact_number': "Enter Contact Number"
		}

	def __init__(self, *args, **kwargs):
		super(StoreForm, self).__init__(*args, **kwargs)
		self.fields['store_name'].widget.attrs.update({'class': 'form-control'})
		self.fields['contact_number'].widget.attrs.update({'class': 'form-control'})

	def clean_store_name(self):
		sn_instance = self.cleaned_data.get("store_name")
		validate = self.__class__._meta.model._default_manager.filter(store_name=sn_instance).exists()
		if validate:
			raise ValidationError(self.validation_messages.get("duplicate_store"))

	def clean_contact_number(self):
		cn_instance = self.cleaned_data.get("contact_number")
		validate = self.__class__._meta.model._default_manager.filter(contact_number=cn_instance).exists()
		if validate:
			raise ValidationError(self.validation_messages.get("dupicate_number"))


class DeliveryBoyForm(forms.ModelForm):
	"""
		Delivery boy signup form
	"""
	validation_messages = {
		"dupicate_number": "Number Already exists with Store"
	}

	class Meta:
		model = DeliveryBoy
		fields = ('number',)

		labels = {
			'number': "Enter Contact Number"
		}
		

	def clean_contact_number(self):
		cn_instance = self.cleaned_data.get("number")
		validate = self.__class__._meta.model._default_manager.filter(number=cn_instance).exists()
		if validate:
			raise ValidationError(self.validation_messages.get("dupicate_number"))


class TaskForm(forms.ModelForm):
	"""
		task creation form store managers
	"""
	validation_messages = {
		"Title_Error": "Please Enter Some Other Title"
	}
	
	class Meta:
		model = Task
		fields = ('title', 'preiority', 'status')

		labels = {
			"title" : "Enter Title",
			"preiority" : "Select Task Preiority",
			"status": "Add Task Intial Status"
		}

	def __init__(self, *args, **kwargs):
		super(TaskForm, self).__init__(*args, **kwargs)
		self.fields['title'].widget.attrs.update({'class': 'form-control'})
		self.fields['preiority'].widget.attrs.update({'class': 'form-control'})
		self.fields['status'].widget.attrs.update({'class': 'form-control'})
	
	def clean_title(self):
		title_instance = self.cleaned_data.get("title")
		validate =  Task.objects.filter(title=title_instance, status=Task.ACCEPTED).exists()
		if validate:
			raise ValidationError(validation_messages["Title_Error"])
		return title_instance

