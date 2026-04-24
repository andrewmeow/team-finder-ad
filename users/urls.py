from django.urls import path, include, reverse_lazy
from .forms import CustomAuthenticationForm
from . import views
app_name = 'users'

urlpatterns = [
    path('register/', views.CustomSignUpView.as_view(), name='register',),
    path('login/', views.CustomLoginView.as_view(
        template_name='registration/login.html',
        form_class=CustomAuthenticationForm,
    ), name='login'),
    path('edit-profile/', views.ProfileUpdateView.as_view(), name='edit-profile'),
    path('change_password/', views.CustomPasswordChangeView.as_view(),
         name='password_change'),
    path('', include('django.contrib.auth.urls')),
    path('list/', views.UserListView.as_view(), name='list'),
    path('<int:page_id>/', views.UserDetailView.as_view(), name='profile'),
]
