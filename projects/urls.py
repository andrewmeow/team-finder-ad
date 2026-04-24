from django.urls import path, include
from . import views
app_name = 'projects'

urlpatterns = [
    path('list/', views.ProjectListView.as_view(), name='project_list'),
    path('<int:pk>/edit', views.ProjectUpdateView.as_view(), name='edit'),
    path('<int:pk>', views.ProjectDetailView.as_view(), name='project-details'),
    path('<int:pk>/complete/', views.ProjectCompleteView.as_view(),
         name='project_complete'),
    path('skills/', views.SkillAutocompleteView.as_view(),
         name='skill_autocomplete'),
    path('<int:pk>/skills/add/', views.ProjectSkillAddView.as_view(),
         name='project_skill_add'),
    path('<int:pk>/skills/<int:skill_id>/remove/',
         views.ProjectSkillRemoveView.as_view(), name='project_skill_remove'),
    path('<int:pk>/toggle-participate/',
         views.ProjectToggleParticipateView.as_view(),
         name='project_toggle_participate'),
    path('create-project',
         views.ProjectCreateView.as_view(), name='create-project'),
]
