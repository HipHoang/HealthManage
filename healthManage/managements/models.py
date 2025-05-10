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
    Exerciser = 1
    Expert = 2

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

class Exerciser(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.user)

    def delete(self, *args, **kwargs):
        self.user.delete()
        super().delete(*args, **kwargs)

class Coach(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.user)

    def delete(self, *args, **kwargs):
        self.user.delete()
        super().delete(*args, **kwargs)

class Activity(BaseModel):
    name = models.CharField(max_length=255)
    description = RichTextField(null=True, blank=True)
    calories_burned = models.FloatField(null=True, blank=True)
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

class HealthRecord(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    bmi = models.FloatField(null=True, blank=True)
    water_intake = models.FloatField(null=True, blank=True)
    steps = models.IntegerField(null=True, blank=True)
    heart_rate = models.IntegerField(null=True, blank=True)
    height = models.FloatField(null=True, blank=True)
    weight = models.FloatField(null=True, blank=True)
    sleep_time = models.FloatField(null=True, blank=True)

    def bmi_calculation(self):
        """Tính chỉ số BMI."""
        if self.height and self.weight:
            return self.weight / (self.height ** 2)
        return None

    def __str__(self):
        return f"{self.user.username} - {self.date}"

    class Meta:
        unique_together = ('user', 'date')


class HealthDiary(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    content = RichTextField()
    feeling = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.date}"

    class Meta:
        unique_together = ('user', 'date')


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
    goal_type = models.CharField(max_length=100, choices=(
        ('weight_loss', 'Giảm cân'),
        ('weight_gain', 'Tăng cân'),
        ('maintain', 'Duy trì'),
        ('muscle_gain', 'Tăng cơ'),
        ('other', 'Khác'),
    ))
    target_weight = models.FloatField(null=True, blank=True)
    target_date = models.DateField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Mục tiêu của {self.user.username} - {self.goal_type}"

class ExpertSpecialization(BaseModel):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        unique_together = ('name',)

class ExpertProfile(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="expert_profile")
    specializations = models.ManyToManyField(ExpertSpecialization, related_name="experts")
    bio = RichTextField(null=True, blank=True)
    experience_years = models.IntegerField(null=True, blank=True)
    consultation_fee = models.FloatField(null=True, blank=True)

    def __str__(self):
        return self.user.username

    class Meta:
        unique_together = ('user',)


class UserConnection(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_connections")
    expert = models.ForeignKey(User, on_delete=models.CASCADE, related_name="expert_connections")
    status = models.CharField(max_length=50, choices=(
        ('pending', 'Đang chờ'),
        ('accepted', 'Đã chấp nhận'),
        ('rejected', 'Đã từ chối'),
        ('blocked', 'Đã chặn')
    ), default='pending')

    def __str__(self):
        return f"Kết nối giữa {self.user.username} và {self.expert.username} - {self.status}"

    class Meta:
        unique_together = ('user', 'expert')
