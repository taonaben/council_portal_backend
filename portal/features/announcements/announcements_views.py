from portal.models import Announcement, AnnouncementComment
from portal.features.announcements.announcements_serializers import (
    AnnouncementSerializer,
    AnnouncementCommentSerializer,
)
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated, IsAdminUser


class announcements_list(generics.ListCreateAPIView):
    serializer_class = AnnouncementSerializer

    def get_permissions(self):
        self.permission_classes = [IsAuthenticated]
        if self.request.method == "POST":
            self.permission_classes = [IsAdminUser]

        return super().get_permissions()

    def get_queryset(self):
        city = self.request.user.city
        current_time = timezone.now()
        return Announcement.objects.filter(
            city=city,
            date_posted__lte=current_time,
        ).exclude(expires_at__lt=current_time)

    def perform_create(self, serializer):
        serializer.save(city=self.request.user.city)


class announcement_detail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Announcement.objects.all()
    serializer_class = AnnouncementSerializer
    lookup_url_kwarg = "announcement_id"

    def get_permissions(self):
        if self.request.method == ["DELETE", "PUT", "PATCH"]:
            self.permission_classes = [IsAdminUser]
        return super().get_permissions()

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        instance.delete()


class announcement_comments_list(generics.ListCreateAPIView):
    serializer_class = AnnouncementCommentSerializer
    permission_classes = [IsAuthenticated]
    lookup_url_kwarg = "announcement_id"

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return AnnouncementComment.objects.none()
        announcement_id = self.kwargs.get("announcement_id")
        return AnnouncementComment.objects.filter(announcement_id=announcement_id)

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user, announcement_id=self.kwargs["announcement_id"]
        )


class announcement_comment_detail(generics.RetrieveUpdateDestroyAPIView):
    queryset = AnnouncementComment.objects.all()
    serializer_class = AnnouncementCommentSerializer
    lookup_url_kwarg = "announcement_comment_id"

    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        """
        Delete the comment only if the requesting user is the comment's author.
        """
        comment = self.get_object()
        if request.user != comment.user and not request.user.is_staff:
            return Response(status=status.HTTP_403_FORBIDDEN)
        self.perform_destroy(comment)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_update(self, serializer):
        """
        Update the comment only if the requesting user is the comment's author.
        """
        comment = self.get_object()
        if comment.user == self.request.user:
            serializer.save()
        else:
            raise PermissionDenied("You do not have permission to edit this comment.")

    def perform_destroy(self, instance):
        instance.delete()
