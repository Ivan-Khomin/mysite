from django.urls import path

from . import views

app_name = 'blog'

urlpatterns = [
    # post view
    path('', views.post_list, name='post_list'),
    # path('', views.PostListView.as_view(), name='post_list'),
    path('tag/<slug:tag_slug>', views.post_list, name='post_list_by_tag'),
    path('<int:year>/<int:month>/<int:day>/<slug:post>/<int:post_id>/', views.post_detail, name='post_detail'),
    path('<int:post_id>/share/', views.post_share, name='post_share'),
    path('login/', views.user_login, name='login'),
    # path('login/', auth_views.LoginView().as_view, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('post-add/', views.post_add, name='post_add'),
    path('post-edit/<int:post_id>/', views.post_edit, name='post_edit'),
    path('post-delete/<int:post_id>/', views.post_delete, name='post_delete'),
    path('post_point_list/<int:post_id>/', views.post_point_list, name='post_point_list'),
    path('post_point_add/<int:post_id>/', views.post_point_add, name='post_point_add'),
    path('post_point_edit/<int:post_point_id>/', views.post_point_edit, name='post_point_edit'),
    path('post_point_delete/<int:post_point_id>/', views.post_point_delete, name='post_point_delete'),
    path('sing-up/', views.sign_up, name='sign-up'),
    path('profile/', views.edit_profile, name='edit_profile'),
    path('add_to_favourite/<int:post_id>/',views.add_to_favourite,name='add_to_favourite'),
    path('delete_from_favourite/<int:post_id>/', views.delete_from_favourite, name='delete_from_favourite'),
    path('favourite-posts/', views.favourite_posts, name='favourite_posts'),
    path('delete_from_favourite_in_dashboard/<int:post_id>/', views.delete_from_favourite_in_dashboard, name='delete_from_favourite_in_dashboard'),
]
