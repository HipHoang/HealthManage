from rest_framework import viewsets, generics, status
from .serializers import *
from managements import paginators
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from .paginators import Pagination
from .perms import *
from rest_framework.parsers import MultiPartParser, JSONParser

class UserViewSet(viewsets.ViewSet, generics.CreateAPIView):
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserSerializer
    pagination_class = Pagination
    parser_classes = [JSONParser, MultiPartParser, ]

    def get_permissions(self):
        if self.action in ["change_password", "update", "current_user"]:
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

    @action(methods=['get'], url_path='current', detail=False)
    def get_current_user(self, request):
        user = request.user
        self.check_object_permissions(request, user)
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

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

    @action(methods=['patch'], url_path='update-info', detail=False)
    def update_info(self, request):
        user = request.user  # lấy user hiện tại
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['get'], url_path='current', detail=False)
    def current_user(self, request):
        user = request.user
        self.check_object_permissions(request, user)
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

class ActivityViewSet(viewsets.ModelViewSet):
    queryset = Activity.objects.all()
    serializer_class = ActivitySerializer
    parser_classes = [JSONParser, MultiPartParser]

    def get_permissions(self):
        if self.request.method in ['GET']:
            return [AllowAny()]
        # Các action chỉ cho Admin hoặc Coach: tạo, cập nhật, xóa
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), AdminPermission(), CoachPermission()]
        # Các action còn lại: xem danh sách, xem chi tiết, recent, search, top-calories...
        return [IsAuthenticated()]

    def get_queryset(self):
        queryset = self.queryset

        # Lọc theo tên (name) của activity nếu có tham số 'q'
        q = self.request.query_params.get('q')
        if q:
            queryset = queryset.filter(name__icontains=q)

        # Lọc theo thể loại (category_id) nếu có tham số 'category_id'
        category_id = self.request.query_params.get('category_id')
        if category_id:
            queryset = queryset.filter(category_id=category_id)

        # Lọc theo mức calo tiêu thụ (calories_burned) nếu có tham số 'calories_min' và 'calories_max'
        calories_min = self.request.query_params.get('calories_min')
        calories_max = self.request.query_params.get('calories_max')
        if calories_min:
            queryset = queryset.filter(calories_burned__gte=calories_min)
        if calories_max:
            queryset = queryset.filter(calories_burned__lte=calories_max)

        return queryset

class WorkoutPlanViewSet(viewsets.ModelViewSet):
    queryset = WorkoutPlan.objects.all()
    serializer_class = WorkoutPlanSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ["create_plan", "user_plans", "weekly_summary"]:
            return [IsAuthenticated()]
        elif self.action in ["plans_by_user"]:
            return [IsAuthenticated(), CoachPermission(), AdminPermission()]
        return super().get_permissions()

    @action(methods=['post'], url_path='create-plan', detail=False)
    def create_plan(self, request):
        """
        Người dùng tạo kế hoạch tập luyện cá nhân.
        """
        user = request.user
        serializer = WorkoutPlanSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=user)
            return Response({"message": "Kế hoạch tập luyện đã được tạo."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['get'], url_path='my-plans', detail=False)
    def user_plans(self, request):
        """
        Lấy các kế hoạch tập luyện của người dùng hiện tại.
        """
        plans = WorkoutPlan.objects.filter(user=request.user)
        serializer = WorkoutPlanSerializer(plans, many=True)
        return Response(serializer.data)

    @action(methods=['get'], url_path='weekly-summary', detail=False)
    def weekly_summary(self, request):
        """
        Thống kê kế hoạch tập luyện trong tuần hiện tại.
        """
        user = request.user
        today = timezone.now().date()
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)

        weekly_plans = WorkoutPlan.objects.filter(user=user, date__range=(start_of_week, end_of_week))
        total_time = sum(
            [plan.sets * plan.reps * plan.activities.count() for plan in weekly_plans if plan.sets and plan.reps])

        serializer = WorkoutPlanSerializer(weekly_plans, many=True)
        return Response({
            "total_sessions": len(weekly_plans),
            "estimated_total_exercise_units": total_time,
            "plans": serializer.data
        })

    @action(methods=['get'], url_path='plans-by-user/(?P<user_id>[^/.]+)', detail=False)
    def plans_by_user(self, request, user_id=None):
        """
        Dành cho Coach/Admin: Xem kế hoạch tập luyện của người dùng cụ thể.
        """
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response({"message": "Người dùng không tồn tại."}, status=status.HTTP_404_NOT_FOUND)

        plans = WorkoutPlan.objects.filter(user=user)
        serializer = WorkoutPlanSerializer(plans, many=True)
        return Response(serializer.data)

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
    serializer_class = HealthRecordSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.user.is_staff and self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]

        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), OwnerPermission()]

        return [IsAuthenticated()]

    def get_queryset(self):
        if self.request.user.is_staff:
            return HealthRecord.objects.all()

        if self.request.user == user.Coach:  # Coach
            return HealthRecord.objects.filter(
                user__in=UserConnection.objects.filter(
                    coach=self.request.user,
                    status='accepted'
                ).values_list('user', flat=True)
            )

        return HealthRecord.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)



class HealthDiaryViewSet(viewsets.ModelViewSet):
    queryset = HealthDiary.objects.all()
    serializer_class = HealthDiarySerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.user.is_staff and self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]

        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), OwnerPermission()]

        # Trường hợp mặc định cho các action còn lại (vd: retrieve của user thường)
        return [IsAuthenticated()]

    def get_queryset(self):
        if self.request.user.is_staff:
            return HealthDiary.objects.all()
        return HealthDiary.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

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
