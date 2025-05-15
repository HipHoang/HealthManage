from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('users', views.UserViewSet, basename='user')
router.register('exerciser', views.ExerciserViewSet, basename='exerciser')
router.register('coach', views.CoachViewSet, basename='coach')
router.register('activity', views.ActivityViewSet, basename='activity')
router.register('workoutplan', views.WorkoutPlanViewSet, basename='workoutplan')
router.register('healthrecord', views.HealthRecordViewSet, basename='healthrecord')

urlpatterns = [
    path('', include(router.urls)),
]




