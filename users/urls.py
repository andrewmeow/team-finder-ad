from django.urls import include, path

from users import views
from users.forms import TeamFinderUserManager

app_name = 'users'

urlpatterns = [
    path('register/', views.SignUpView.as_view(), name='register',),
    path('login/', views.TeamFinderLoginView.as_view(
        template_name='registration/login.html',
        form_class=TeamFinderUserManager,
    ), name='login'),
    path('edit-profile/', views.ProfileUpdateView.as_view(), name='edit-profile'),
    path('change_password/', views.TeamFinderPasswordChangeView.as_view(),
         name='password_change'),
    path('', include('django.contrib.auth.urls')),
    path('list/', views.UserListView.as_view(), name='list'),
    path('<int:page_id>/', views.UserDetailView.as_view(), name='profile'),
]
