from .models import *
from rest_framework import viewsets, generics, status
from .serializers import *
from managements import serializers, paginators
import json
from cloudinary.uploader import upload
from django.db.models import Q
from django.shortcuts import render
from rest_framework.decorators import action, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from .paginators import Pagination
from .perms import *
from rest_framework.parsers import MultiPartParser, JSONParser
from rest_framework.request import Request


class UserViewSet(viewsets.ViewSet, generics.CreateAPIView):
    queryset = User.objects.select_related('user')
    serializer_class = UserSerializer
    pagination_class = Pagination
    parser_classes = [JSONParser, MultiPartParser, ]

    def get_permissions(self):
        if self.action in ["change_password", "get_current_user"]:
            return [OwnerPermission()]
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

            if hasattr(user, 'teacher') and user.teacher.must_change_password:
                teacher = user.teacher
                teacher.must_change_password = False
                teacher.password_reset_time = None
                teacher.save(update_fields=['must_change_password', 'password_reset_time'])

            return Response({"message": "Mật khẩu đã được thay đổi thành công."}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ExerciserViewSet(viewsets.ViewSet, generics.CreateAPIView):
    queryset = Exerciser.objects.select_related('user')
    serializer_class = ExerciserSerializer
    pagination_class = Pagination
    parser_classes = [JSONParser, MultiPartParser, ]

    def get_queryset(self):
        query = self.queryset
        q = self.request.query_params.get("search")
        if q:
            query = query.filter(Q(user__first_name__icontains=q) | Q(user__last_name__icontains=q))
        return query

class CoachViewSet(viewsets.ViewSet, generics.CreateAPIView):
    queryset = Coach.objects.select_related('user')
    serializer_class = CoachSerializer
    pagination_class = Pagination
    parser_classes = [JSONParser, MultiPartParser, ]

    def get_queryset(self):
        query = self.queryset
        q = self.request.query_params.get("search")
        if q:
            query = query.filter(Q(user__first_name__icontains=q) | Q(user__last_name__icontains=q))
        return query

class ActivityViewSet(viewsets.ModelViewSet):
    queryset = Activity.objects.all()
    serializer_class = ActivitySerializer
    parser_classes = [JSONParser, MultiPartParser]

    def get_permissions(self):
        if self.action == "create":
            return [IsAuthenticated()]
        elif self.action in ["update", "destroy", "lock_unlock_comments"]:
            return [OwnerPermission(), AdminPermission()]
        return super().get_permissions()

class WorkoutPlanViewSet(viewsets.ModelViewSet):
    queryset = WorkoutPlan.objects.all()
    serializer_class = WorkoutPlanSerializer
    permission_classes = [IsAuthenticated]


class MealPlanViewSet(viewsets.ModelViewSet):
    queryset = MealPlan.objects.all()
    serializer_class = MealPlanSerializer
    permission_classes = [IsAuthenticated]


class HealthRecordViewSet(viewsets.ModelViewSet):
    queryset = HealthRecord.objects.all()
    serializer_class = HealthRecordSerializer
    permission_classes = [IsAuthenticated]

class HealthDiaryViewSet(viewsets.ModelViewSet):
    queryset = HealthDiary.objects.all()
    serializer_class = HealthDiarySerializer
    permission_classes = [IsAuthenticated]


class ChatMessageViewSet(viewsets.ModelViewSet):
    queryset = ChatMessage.objects.all()
    serializer_class = ChatMessageSerializer
    permission_classes = [IsAuthenticated]


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
