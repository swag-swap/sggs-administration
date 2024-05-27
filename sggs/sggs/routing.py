from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/session/(?P<session_id>\w+)/test/(?P<test_id>\w+)/', consumers.TestConsumer.as_asgi()),
    re_path(r'ws/session/(?P<session_id>\w+)/test/(?P<test_id>\w+)/teacher/$', consumers.TeacherDashboardConsumer.as_asgi()),
]