import logging

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.files.images import ImageFile
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from rest_framework import viewsets, generics, parsers, status, mixins, renderers, filters
from rest_framework.decorators import detail_route
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from taggit.models import Tag
from wagtail.wagtailimages.models import Image
from wagtail.wagtailsearch.backends import get_search_backend

from core.models import FollowUser, Event, Job
from core.serializers import TagSerializer
from core.view_helpers import retrieve_with_perms, get_search_queryset
from core.views import (CaseInsensitiveOrderingFilter, CommonViewSetMixin, FormCreateView, FormUpdateView,
                        SmallResultSetPagination)
from .models import FeaturedContentItem, MemberProfile
from .serializers import (FeaturedContentItemSerializer, UserMessageSerializer, MemberProfileSerializer)

logger = logging.getLogger(__name__)

search = get_search_backend()


"""
Contains wagtail related views
"""


class ToggleFollowUser(APIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (TemplateHTMLRenderer, JSONRenderer)

    def post(self, request, *args, **kwargs):
        logger.debug("POST with request data: %s", request.data)
        username = request.data['username']
        source = request.user
        target = User.objects.get(username=username)
        follow_user, created = FollowUser.objects.get_or_create(source=source, target=target)
        if created:
            target.following.add(follow_user)
        else:
            follow_user.delete()
        return Response({'following': created})


class TagListView(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    pagination_class = SmallResultSetPagination
    renderer_classes = (renderers.JSONRenderer,)

    def get_queryset(self):
        query = self.request.query_params.get('query')
        queryset = Tag.objects.all()
        if query:
            queryset = queryset.filter(name__icontains=query)
        return queryset.order_by('name')


class MemberProfileFilter(filters.BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        if view.action != 'list':
            return queryset
        query_params = request.query_params
        qs = query_params.get('query')
        tags = query_params.getlist('tags')
        return get_search_queryset(qs, queryset, tags=tags)


class ProfileViewSet(CommonViewSetMixin, viewsets.ModelViewSet):
    lookup_field = 'user__username'
    lookup_url_kwarg = 'username'
    lookup_value_regex = '[\w\.\-@]+'
    serializer_class = MemberProfileSerializer
    queryset = MemberProfile.objects.public().with_institution().order_by('id')
    pagination_class = SmallResultSetPagination
    filter_backends = (CaseInsensitiveOrderingFilter, MemberProfileFilter)
    ordering_fields = ('user__username', 'user__last_name', 'user__email',)

    def retrieve(self, request, *args, **kwargs):
        return retrieve_with_perms(self, request, *args, **kwargs)

    @detail_route(methods=['post'])
    @method_decorator(login_required)
    def message(self, request, *args, **kwargs):
        logger.debug("POST with request data: %s", request.data)
        # FIXME: perhaps we should just send an email directly instead of caching in the db.
        serializer = UserMessageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MemberProfileImageUploadView(generics.CreateAPIView):
    parser_classes = (parsers.MultiPartParser, parsers.FormParser,)
    queryset = MemberProfile.objects.all()

    def create(self, request, *args, **kwargs):
        file_obj = request.data['file']
        username = request.user.username
        member_profile = get_object_or_404(MemberProfile, user__username=username)
        image = Image(title=file_obj.name, file=ImageFile(file_obj), uploaded_by_user=request.user)
        image.save()
        member_profile.picture = image
        member_profile.save()
        return Response(data=image.get_rendition('fill-150x150').url, status=200)


class FeaturedContentListAPIView(generics.ListAPIView):
    serializer_class = FeaturedContentItemSerializer
    queryset = FeaturedContentItem.objects.all()
    pagination_class = SmallResultSetPagination


class EventCreateView(FormCreateView):
    model = Event


class EventUpdateView(FormUpdateView):
    model = Event


class JobCreateView(FormCreateView):
    model = Job


class JobUpdateView(FormUpdateView):
    model = Job


class ProfileUpdateView(FormUpdateView):
    model = MemberProfile
    slug_field = 'user__username'
    slug_url_kwarg = 'username'
