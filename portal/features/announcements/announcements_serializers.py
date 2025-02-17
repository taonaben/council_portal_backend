from rest_framework import serializers
from portal.models import Announcement, AnnouncementComment
from portal.models import City


class AnnouncementSerializer(serializers.ModelSerializer):

    comments_count = serializers.SerializerMethodField(method_name="get_comments_count")

    def get_comments_count(self, obj):
        return obj.announcement_comments.count()

    class Meta:
        model = Announcement
        fields = (
            "id",
            "title",
            "message",
            "display_image",
            "city",
            "comments_count",
            "up_votes",
            "date_posted",

            "expires",
            
            "expires_at",
        )
        read_only_fields = (
            "id",
            "city",
            "date_posted",
            "comments_count",
            "up_votes",
            "expires_at",
        )


class AnnouncementCommentSerializer(serializers.ModelSerializer):

    class Meta:
        model = AnnouncementComment
        fields = (
            "id",
            "announcement",
            "user",
            "comment",
            "up_votes",
            "created_at",
        )
        read_only_fields = ("id", "announcement", "up_votes", "user", "created_at")
