from rest_framework import serializers
from rest_framework.serializers import *
from managements.models import *


class UserSerializer(ModelSerializer):

    def create(self, validated_data):
        data = validated_data.copy()
        u = User(**data)
        u.role = 0
        u.set_password(u.password)
        u.save()
        return u

    class Meta:
        model = User
        fields = ["id", "username", "password", "avatar", "first_name", "last_name", "email", "role", 'birthday']
        extra_kwargs = {
            'password': {
                'write_only': True,
                'required': False
            }
        }

class ChangePasswordSerializer(ModelSerializer):
    current_password = CharField(write_only=True, required=True)
    new_password = CharField(write_only=True, required=True)

    def validate_current_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Mật khẩu hiện tại không đúng.")
        return value

class ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = ['id', 'name', 'description', 'calories_burned', 'image']

class WorkoutPlanSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    activities = ActivitySerializer(many=True, read_only=True) # Nest Activity info
    class Meta:
        model = WorkoutPlan
        fields = ['id', 'user', 'name', 'date', 'activities', 'description', 'sets', 'reps']

class MealPlanSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    class Meta:
        model = MealPlan
        fields = ['id', 'user', 'name', 'date', 'description', 'calories_intake']

class CoachProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    class Meta:
        model = CoachProfile
        fields = ['id', 'user', 'bio', 'specialties', 'years_of_experience', 'certifications']

class HealthRecordSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    class Meta:
        model = HealthRecord
        fields = ['id', 'user', 'bmi', 'water_intake', 'steps', 'heart_rate',
                  'height', 'weight', 'sleep_time', 'date']
        read_only_fields = ['bmi']

class HealthDiarySerializer(serializers.ModelSerializer):
    user = UserSerializer()
    class Meta:
        model = HealthDiary
        fields = ['id', 'user', 'date', 'content', 'feeling']

class ChatMessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer()
    receiver = UserSerializer()
    class Meta:
        model = ChatMessage
        fields = ['id', 'sender', 'receiver', 'message', 'timestamp', 'is_read']

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']

class UserGoalSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = UserGoal
        fields = ['id', 'user', 'goal_type', 'target_weight', 'target_date', 'description']

class UserConnectionSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    coach = UserSerializer()
    class Meta:
        model = UserConnection
        fields = ['id', 'user', 'coach', 'status']
