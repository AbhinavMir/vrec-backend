from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models

class UserManager(BaseUserManager):
    def create_user(self, email, name, password=None):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, name=name)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password=None):
        user = self.create_user(email, name, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)
    is_subscription_active = models.BooleanField(default=False)
    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return self.email
    
    def change_password(self, old_password, new_password):
        if not self.check_password(old_password):
            raise ValueError('Old password is incorrect')
        
        self.set_password(new_password)
        self.save()

class Transcription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    length = models.IntegerField() # length of transcript word wise
    transcript = models.TextField(null=True)
 
    def __str__(self):
        return f"Transcription for {self.user.email} on {self.date}"

class Summary(models.Model):
    MOOD_CHOICES = (
        ('happy', 'Happy'),
        ('sad', 'Sad'),
        ('neutral', 'Neutral'),
        ('angry', 'Angry'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    mood = models.CharField(max_length=10, choices=MOOD_CHOICES)
    summary = models.TextField()
    date = models.DateField()

    def __str__(self):
        return f"Summary for {self.user.email} on {self.date}"
