from django.urls import path
from .views import Login, Logout, Signup, home
from events import views
from django.conf import settings
from django.conf.urls.static import static

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
    path('profile/edit/',views.profile_edit ,name='profile-edit'),
    path('profile/password_change/',views.change_password ,name='change-password'),
    path('profile/<int:user_id>',views.profile_detail ,name='profile-detail'),
    path('event/<int:booked_id>/<int:event_id>/cancel/',views.cancel_event ,name='cancel-event'),
    path('profile/<int:user_id>/follow/',views.follow ,name='profile-follow'),
    path('profile/<int:user_id>/like/',views.like ,name='profile-like'),
    path('events/',views.ev_li ,name='ev-li'),

]

if settings.DEBUG:
    urlpatterns+=static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns+=static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)