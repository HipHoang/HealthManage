from rest_framework import viewsets, generics, status
from .serializers import *
from managements import paginators
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from .paginators import Pagination
from .perms import *
from rest_framework.parsers import MultiPartParser, JSONParser

class UserViewSet(viewsets.ViewSet, generics.CreateAPIView, generics.RetrieveAPIView):
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserSerializer
    pagination_class = Pagination
    parser_classes = [JSONParser, MultiPartParser, ]

    def get_permissions(self):
        if self.action in ["change_password", "retrieve", "update"]:
            return [OwnerPermission()]
        elif self.action == "create":
            return [AllowAny()]
        return [IsAuthenticated()]

    @action(methods=['get'], url_path='all-users', detail=False)
    def get_all_users(self, request):
        self.check_permissions(request)
        queryset = User.objects.filter(is_active=True)

        pagination_class = paginators.Pagination()
        paginated_queryset = pagination_class.paginate_queryset(queryset, request, view=self)

        serializer = UserSerializer(paginated_queryset, many=True)
        return pagination_class.get_paginated_response(serializer.data)

    @action(methods=['patch'], url_path='change-password', detail=False)
    def change_password(self, request):
        user = request.user
        self.check_object_permissions(request, user)

        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user.set_password(serializer.validated_data['new_password'])
            user.save(update_fields=['password'])
            return Response({"message": "Mật khẩu đã được thay đổi thành công."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['patch'], url_path='update-info', detail=True)
    def update_info(self, request):
        user = self.get_object()
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ActivityViewSet(viewsets.ModelViewSet):
    queryset = Activity.objects.all()
    serializer_class = ActivitySerializer
    parser_classes = [JSONParser, MultiPartParser]

class WorkoutPlanViewSet(viewsets.ModelViewSet):
    queryset = WorkoutPlan.objects.all()
    serializer_class = WorkoutPlanSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ["create_plan", "weekly_summary"]:
            return [IsAuthenticated()]
        return super().get_permissions()

    @action(methods=['post'], url_path='create-plan', detail=False)
    def create_plan(self, request):
        """
        Tạo kế hoạch tập luyện.
        """
        user = request.user
        serializer = WorkoutPlanSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=user)
            return Response({"message": "Kế hoạch tập luyện đã được tạo."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MealPlanViewSet(viewsets.ModelViewSet):
    queryset = MealPlan.objects.all()
    serializer_class = MealPlanSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ["create_meal_plan", "suggest_meals"]:
            return [IsAuthenticated()]
        return super().get_permissions()

    @action(methods=['post'], url_path='create-meal-plan', detail=False)
    def create_meal_plan(self, request):
        """
        Tạo thực đơn dinh dưỡng.
        """
        user = request.user
        serializer = MealPlanSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=user)
            return Response({"message": "Thực đơn dinh dưỡng đã được tạo."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class HealthRecordViewSet(viewsets.ModelViewSet, generics.RetrieveAPIView):
    queryset = HealthRecord.objects.all()
    serializer_class = HealthRecordSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ["add_record", "view_record", "log_daily_stats", "retrieve", "update"]:
            return [IsAuthenticated(), OwnerPermission()]
        return [IsAuthenticated()]

    @action(methods=['post'], url_path='add-record', detail=False)
    def add_record(self, request):
        """
        Thêm hồ sơ sức khỏe.
        """
        user = request.user
        serializer = HealthRecordSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=user)
            return Response({"message": "Hồ sơ sức khỏe đã được cập nhật."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['get'], url_path='view-record', detail=False)
    def view_record(self, request):
        """
        Xem hồ sơ sức khỏe của người dùng.
        """
        user = request.user
        record = HealthRecord.objects.filter(user=user).first()
        if record:
            serializer = HealthRecordSerializer(record)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({"message": "Hồ sơ sức khỏe không tồn tại."}, status=status.HTTP_404_NOT_FOUND)

class HealthDiaryViewSet(viewsets.ModelViewSet):
    queryset = HealthDiary.objects.all()
    serializer_class = HealthDiarySerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ["create", "my_diary", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), OwnerPermission()]
        return [IsAuthenticated()]

class ChatMessageViewSet(viewsets.ModelViewSet):
    queryset = ChatMessage.objects.all()
    serializer_class = ChatMessageSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ["send_message", "list", "retrieve"]:
            return [IsAuthenticated()]
        return super().get_permissions()

    @action(methods=['post'], url_path='send-message', detail=False)
    def send_message(self, request):
        """
        Gửi tin nhắn cho huấn luyện viên hoặc chuyên gia dinh dưỡng.
        """
        user = request.user
        receiver_id = request.data.get('receiver_id')
        message = request.data.get('message')

        receiver = User.objects.filter(id=receiver_id).first()
        if not receiver:
            return Response({"message": "Huấn luyện viên hoặc chuyên gia không tồn tại."},
                            status=status.HTTP_400_BAD_REQUEST)

        chat_message = ChatMessage(sender=user, receiver=receiver, message=message)
        chat_message.save()

        return Response({"message": "Tin nhắn đã được gửi."}, status=status.HTTP_201_CREATED)

class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticated]


class UserGoalViewSet(viewsets.ModelViewSet):
    queryset = UserGoal.objects.all()
    serializer_class = UserGoalSerializer
    permission_classes = [IsAuthenticated]

class UserConnectionViewSet(viewsets.ModelViewSet):
    queryset = UserConnection.objects.all()
    serializer_class = UserConnectionSerializer
    permission_classes = [IsAuthenticated]
