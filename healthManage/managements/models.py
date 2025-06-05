from django.utils import timezone
from django.db import models
from django.contrib.auth.models import AbstractUser
from ckeditor.fields import RichTextField
from cloudinary.models import CloudinaryField
from enum import IntEnum

class BaseModel(models.Model):
    created_date = models.DateField(auto_now_add=True, null=True)
    updated_date = models.DateField(auto_now=True, null=True)
    active = models.BooleanField(default=True)

    class Meta:
        abstract = True
        ordering = ['-id']

class Role(IntEnum):
    Admin = 0
    Exerciser_Self_Help = 1
    Exerciser_With_Coach = 2
    Coach = 3

    @classmethod
    def choices(cls):
        return [(role.value, role.name.capitalize()) for role in cls]

class User(AbstractUser):
    avatar = CloudinaryField('avatar', null=True, blank=True, folder='avatar' ,default='')
    email = models.EmailField(unique=True, null=False, max_length=255)
    role = models.IntegerField(
        choices=Role.choices(),
        default=Role.Admin.value
    )

    def __str__(self):
        return self.username

class Activity(BaseModel):
    name = models.CharField(max_length=255)
    description = RichTextField(null=True, blank=True)
    calories_burned = models.FloatField(null=True, blank=True)
    time = models.IntegerField(null=True, blank=True)
    image = CloudinaryField('activity_image', null=True, blank=True)

    def __str__(self):
        return self.name

class WorkoutPlan(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    date = models.DateField()
    activities = models.ManyToManyField(Activity)
    description = RichTextField(null=True, blank=True)
    sets = models.IntegerField(null=True, blank=True)
    reps = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.name

class MealPlan(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    date = models.DateField()  # Removed default=timezone.now
    description = RichTextField(null=True, blank=True)
    calories_intake = models.FloatField(null=True, blank=True)

    def __str__(self):
        return self.name

class CoachProfile(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = RichTextField(null=True, blank=True, help_text="Giới thiệu bản thân")
    specialties = models.CharField(max_length=255, help_text="Ví dụ: Gym, Yoga, Cardio...")
    years_of_experience = models.PositiveIntegerField(default=0)
    certifications = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.user.username

class HealthRecord(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    water_intake = models.FloatField(null=True, blank=True)
    steps = models.IntegerField(null=True, blank=True)
    heart_rate = models.IntegerField(null=True, blank=True)
    height = models.FloatField(null=True, blank=True)
    weight = models.FloatField(null=True, blank=True)
    bmi = models.FloatField(editable=False, blank=True, null=True)

    def save(self, *args, **kwargs):
        try:
            self.bmi = round(self.weight / ((self.height / 100) ** 2), 2)
        except (TypeError, ZeroDivisionError):
            self.bmi = None
        super().save(*args, **kwargs)

class HealthDiary(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    content = RichTextField()
    feeling = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.date}"

    class Meta:
        unique_together = ('user', 'date')
        ordering = ['-id']

class ChatMessage(BaseModel):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.sender.username} to {self.receiver.username} - {self.timestamp}"

    class Meta:
        ordering = ['timestamp']
        unique_together = ('sender', 'receiver', 'timestamp')


class Tag(BaseModel):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class UserGoal(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    goal_type = models.TextField(null=True, blank=True)
    target_weight = models.FloatField(null=True, blank=True)
    target_date = models.DateField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Mục tiêu của {self.user.username} - {self.goal_type}"

class UserConnection(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_connections")
    coach = models.ForeignKey(User, on_delete=models.CASCADE, related_name="coach_connections")
    status = models.CharField(max_length=50, choices=(
        ('pending', 'Đang chờ'),
        ('accepted', 'Đã chấp nhận'),
        ('rejected', 'Đã từ chối'),
        ('blocked', 'Đã chặn')
    ), default='pending')

    def __str__(self):
        return f"Kết nối giữa {self.user.username} và {self.coach.username} - {self.status}"

    class Meta:
        unique_together = ('user', 'coach')
