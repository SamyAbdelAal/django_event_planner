from django.urls import path
from .views import Login, Logout, Signup, home
from events import views

urlpatterns = [
	path('', home, name='home'),
    path('signup/', Signup.as_view(), name='signup'),
    path('login/', Login.as_view(), name='login'),
    path('logout/', Logout.as_view(), name='logout'),

    path('dashboard/',views.dashboard ,name='dashboard-list'),
    path('event/create/',views.event_create ,name='event-create'),
    path('event/<int:event_id>/edit/',views.event_edit ,name='event-edit'),
    path('event/<int:event_id>/detail/',views.event_detail ,name='event-detail'),
    path('event/<int:event_id>/booked/',views.event_booked ,name='event-booked'),
    path('event/list',views.event_list ,name='event-list'),

]