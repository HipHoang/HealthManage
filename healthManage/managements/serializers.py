from rest_framework import serializers
from rest_framework.serializers import *
from managements.models import *
from cloudinary.uploader import upload
from cloudinary.exceptions import Error


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
        fields = ["id", "username", "password", "avatar", "first_name", "last_name", "email", "role"]
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

class ExerciserSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Exerciser
        fields = ['id', 'user']

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user_data['role'] = 1
        user_data['is_active'] = False
        avatar = user_data.pop('avatar', None)
        password = user_data.get('password')

        if not password:
            raise ValidationError({"password": "Yêu cầu mật khẩu."})

        if avatar:
            try:
                avatar_result = upload(avatar, folder="avatar")
                user_data['avatar'] = avatar_result.get('secure_url')
            except Error as e:
                raise ValidationError({"avatar": f"Lỗi đăng tải avatar: {str(e)}"})

        user = User.objects.create_user(
            username=user_data.get('username'),
            password=password,
            first_name=user_data.get('first_name'),
            last_name=user_data.get('last_name'),
            email=user_data.get('email'),
            avatar=user_data.get('avatar'),
            role=user_data.get('role'),
            is_active=user_data.get('is_active')
        )

        exerciser = Exerciser.objects.create(user=user, **validated_data)
        return exerciser

class CoachSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Coach
        fields = ['id', 'user']

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user_data['role'] = 2
        user_data['is_active'] = False
        avatar = user_data.pop('avatar', None)
        password = user_data.get('password')

        if not password:
            raise ValidationError({"password": "Yêu cầu mật khẩu."})

        if avatar:
            try:
                avatar_result = upload(avatar, folder="avatar")
                user_data['avatar'] = avatar_result.get('secure_url')
            except Error as e:
                raise ValidationError({"avatar": f"Lỗi đăng tải avatar: {str(e)}"})

        user = User.objects.create_user(
            username=user_data.get('username'),
            password=password,
            first_name=user_data.get('first_name'),
            last_name=user_data.get('last_name'),
            email=user_data.get('email'),
            avatar=user_data.get('avatar'),
            role=user_data.get('role'),
            is_active=user_data.get('is_active')
        )

        coach = Coach.objects.create(user=user, **validated_data)
        return coach

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

class HealthRecordSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    class Meta:
        model = HealthRecord
        fields = ['id', 'user', 'bmi', 'water_intake', 'steps', 'heart_rate',
                  'height', 'weight', 'sleep_time', 'birthday']
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
