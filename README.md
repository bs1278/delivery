#### Delivery is Simple Delivery management Application.
#### Store manager can create task for delivery boys.
#### Store manager can cancel task which not yet accpeted by delivery boy.
#### Store manager can view all tasks list and thier status on dashboard.

#### Deliver boy can Accept New Tasks from store.
#### Deliver boy can reject his/her task once accepted.
#### Deliver boy can view all his Past accepted tasks and completed tasks on dashboard.
#### Deliver boy can only accpet three tasks in his account if he accept more he/she needs to perform action on old tasks.





#### Setting up


Fork the project to your personal account and get a local copy on your machine.
Change into the project folder.


Setup Virtual Environment for Delivery app
```sh
$ pyvenv venv (creates new virtualenv for project)
$ source venv/bin/activate (activate virtualenv assumeing using ubuntu)
$ pip install -r requirements.txt  (install dependencies)
```

Make sure to create migrations, create tables in db, and create a superuser to have an admin dashboard.

```sh
$ python manage.py makemigrations (creates migration files based on your models)
$ python manage.py migrate (creates the tables in your db based on the migration files)
$ python manage.py createsuperuser (creates a superuser for your application in the db)
$ python manage.py runserver (run server)
```
##### for storemanager 
##### username : omega
##### password :ASDFGhjkl1@


##### for deliver boy
##### username : deliverboy-1
##### password : ASDFGhjkl1@

Now you should be able to view your app at http://127.0.0.1:8000 and to view your admin dashboard use 
http://127.0.0.1:8000/admin/.
