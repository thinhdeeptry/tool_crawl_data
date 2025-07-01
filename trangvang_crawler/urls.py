from django.urls import path
from . import views

urlpatterns = [
    path('task/<int:task_id>/export/', views.export_task_to_excel, name='export_task_to_excel'),
    path('task/<int:task_id>/run/', views.run_crawl_task, name='run_crawl_task'),
]