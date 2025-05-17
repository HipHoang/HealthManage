from django.contrib import admin
from django.db.models import Count
from django.template.response import TemplateResponse
from django.urls import path
from managements.models import *

from oauth2_provider.models import AccessToken, Application

class MyAdminSite(admin.AdminSite):
    site_header = 'Health Management Administration'

    def get_urls(self):
        return [path('managements-stats/', self.managements_stats)] + super().get_urls()

    def managements_stats(self, request):
        stats = Activity.objects.annotate(activity_count=Count('active')).values('name', 'activity_count')
        stat = HealthRecord.objects.annotate(re_count=Count('active')).values('bmi', 're_count', 'water_intake','height', 'weight', 'heart_rate', 'steps','date')

        # Thêm thống kê số lượng mục tiêu theo loại
        goal_stats = UserGoal.objects.values('goal_type').annotate(goal_count=Count('id')).order_by()

        # Thêm thống kê số lượng nhật ký sức khỏe của mỗi người dùng
        diary_stats = HealthDiary.objects.values('user__username').annotate(diary_count=Count('id')).order_by()

        # Thêm thống kê số lượng hoạt động
        activity_stats = Activity.objects.annotate(activity_count=Count('workoutplan')).values('name',
                                                                                               'activity_count').order_by()

        return TemplateResponse(request, 'admin/managements-stats.html', {
            'stats': stats,
            'stat': stat,
            'goal_stats': goal_stats,
            'diary_stats': diary_stats,
            'activity_stats': activity_stats,  # Thêm dòng này
        })

class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "role", "is_staff", "is_active")
    list_filter = ("role", "is_staff", "is_active")
    search_fields = ("username", "email")
    ordering = ("id",)

class ActivityAdmin(admin.ModelAdmin):
    list_display = ("name", "calories_burned", "active")
    search_fields = ("name", "description")
    list_filter = ("active",)


class WorkoutPlanAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "date")
    search_fields = ("name", "user__username")
    list_filter = ("date", "user")


class MealPlanAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "date", "calories_intake")
    search_fields = ("name", "user__username")
    list_filter = ("date", "user")

class HealthRecordAdmin(admin.ModelAdmin):
    list_display = ("user", "bmi", "water_intake", "steps", "heart_rate")
    search_fields = ("user__username",)  # Tìm kiếm theo tên người dùng
    list_filter = ("user",)
    readonly_fields = ("bmi",)

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == "user":
            kwargs["queryset"] = User.objects.filter(role=1)
        return super().formfield_for_dbfield(db_field, **kwargs)

class CoachProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "bio", "specialties", "years_of_experience", "certifications",)
    search_fields = ("user__username",)
    list_filter = ("user",)

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == "user":
            kwargs["queryset"] = User.objects.filter(role=2)
        return super().formfield_for_dbfield(db_field, **kwargs)


class HealthDiaryAdmin(admin.ModelAdmin):
    list_display = ("user", "date", "feeling")
    search_fields = ("user__username", "content")
    list_filter = ("user", "date")
    date_hierarchy = "date"

class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ("sender", "receiver", "timestamp", "is_read")
    search_fields = ("sender__username", "receiver__username", "message")
    list_filter = ("is_read", "sender", "receiver", "timestamp")
    date_hierarchy = "timestamp"



class TagAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)

class UserGoalAdmin(admin.ModelAdmin):
    list_display = ("user", "goal_type", "target_date")
    search_fields = ("user__username", "goal_type")
    list_filter = ("user", "goal_type", "target_date")



class UserConnectionAdmin(admin.ModelAdmin):
    list_display = ("user", "coach", "status")
    search_fields = ("user__username", "coach__username")
    list_filter = ("user", "coach", "status")

admin_site = MyAdminSite(name='admin')

admin_site.register(User, UserAdmin)
admin_site.register(HealthRecord, HealthRecordAdmin)
admin_site.register(CoachProfile, CoachProfileAdmin)
admin_site.register(Activity, ActivityAdmin)
admin_site.register(WorkoutPlan, WorkoutPlanAdmin)
admin_site.register(HealthDiary, HealthDiaryAdmin)
admin_site.register(ChatMessage, ChatMessageAdmin)
admin_site.register(Tag, TagAdmin)
admin_site.register(UserGoal, UserGoalAdmin)
admin_site.register(UserConnection, UserConnectionAdmin)
admin_site.register(MealPlan, MealPlanAdmin)
admin_site.register(Application)
admin_site.register(AccessToken)
