from django.contrib import admin
from django.db.models import Count
from django.template.response import TemplateResponse
from django.urls import path

from managements.models import *


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


admin_site = MyAdminSite(name='admin')

admin_site.register(User)
admin_site.register(HealthRecord)
admin_site.register(Activity)
admin_site.register(WorkoutPlan)
admin_site.register(HealthDiary)
admin_site.register(ChatMessage)
admin_site.register(Tag)
admin_site.register(UserGoal)
admin_site.register(ExpertSpecialization)
admin_site.register(ExpertProfile)
admin_site.register(UserConnection)
