from django.conf.urls import url, include
from django.views.generic import TemplateView
from . import views
from rest_framework.routers import SimpleRouter
from core.view_helpers import create_edit_routes

router = SimpleRouter()
router.register(r'events', views.EventViewSet, base_name='event')
router.register(r'jobs', views.JobViewSet, base_name='job')
router.register(r'tags', views.TagViewSet, base_name='tag')

urlpatterns = [
    url(r'^$', TemplateView.as_view(template_name='home/index.jinja'), name='index'),
    url(r'^', include(router.urls)),
    url(r'^resources', TemplateView.as_view(template_name='home/resources.jinja'),
        name='resources'),
    url(r'^community', TemplateView.as_view(template_name='home/community.jinja'), name='community'),
]

urlpatterns += router.urls

edit_route_form_data = {'lookup_field': 'pk', 'lookup_regex': r'\d+', 'app_name': 'home'}
for base_name in ['job', 'event']:
    urlpatterns += create_edit_routes(base_name=base_name, prefix=base_name + 's', **edit_route_form_data)
