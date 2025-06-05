from rest_framework import serializers
from rest_framework.serializers import *
from managements.models import *

class UserSerializer(ModelSerializer):
    confirm_password = serializers.CharField(write_only=True, required=True)
    avatar_url = serializers.SerializerMethodField()

    def get_avatar_url(self, user):
        if user.avatar and hasattr(user.avatar, 'url'):
            return user.avatar.url
        return None

    def validate(self, attrs):
        if attrs.get('password') != attrs.get('confirm_password'):
            raise serializers.ValidationError({"password": "Mật khẩu xác nhận không khớp."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('confirm_password')  # Xoá confirm_password trước khi lưu
        u = User(**validated_data)
        u.role = validated_data.get('role', 0) # mặc định
        u.set_password(validated_data['password'])  # mã hoá mật khẩu
        u.save()
        return u

    class Meta:
        model = User
        fields = ["id", "username", "password", "confirm_password", "avatar", "avatar_url", "first_name", "last_name", "email", "role"]
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

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError("Mật khẩu mới và mật khẩu xác nhận không khớp.")
        return attrs

class ActivitySerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    def get_image_url(self, obj):
        if obj.image and hasattr(obj.image, 'url'):
            return obj.image.url  # Cloudinary đã là full URL
        return None

    class Meta:
        model = Activity
        fields = ['id', 'name', 'description', 'calories_burned', 'image_url']

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
    user = UserSerializer(read_only=True)
    class Meta:
        model = HealthRecord
        fields = ['id', 'user', 'bmi', 'water_intake', 'steps', 'heart_rate', 'height', 'weight', 'date']
        read_only_fields = ['bmi']

class HealthDiarySerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
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
        read_only_fields = ['user']

class UserConnectionSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    coach = UserSerializer()
    class Meta:
        model = UserConnection
        fields = ['id', 'user', 'coach', 'status']
