from django.db import models

# Create your models here.

class Appointment(models.Model):
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    service = models.CharField(max_length=100)
    chiropractor = models.CharField(max_length=100)
    date = models.DateField()
    time = models.TimeField()




class Admin(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    image = models.ImageField(upload_to='photos/')
    password = models.CharField(max_length=256)    
    
  


class User(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=256)    
    


class SupportTickets(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
