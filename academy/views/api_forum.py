from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from ..models import ForumTopic, ForumReply, Course
from ..serializers import ForumTopicSerializer, ForumReplySerializer, ForumTopicCreateSerializer

class ForumViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = ForumTopic.objects.all()

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ForumTopicCreateSerializer
        return ForumTopicSerializer

    def perform_create(self, serializer):
        topic = serializer.save(user=self.request.user)
        # Ensure we return the full serializer data in response (create returns partial otherwise)
        # But DRF default create returns serializer.data which is the CreateSerializer
        # We might want to return the detailed one.

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        topic = serializer.save(user=self.request.user)
        # Return full representation
        read_serializer = ForumTopicSerializer(topic)
        headers = self.get_success_headers(read_serializer.data)
        return Response(read_serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=True, methods=['get'])
    def replies(self, request, pk=None):
        topic = self.get_object()
        replies = topic.replies.all()
        serializer = ForumReplySerializer(replies, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def reply(self, request, pk=None):
        topic = self.get_object()
        content = request.data.get('content')
        if not content:
            return Response({'error': 'Contenido requerido'}, status=status.HTTP_400_BAD_REQUEST)

        reply = ForumReply.objects.create(
            topic=topic,
            user=request.user,
            content=content
        )
        return Response(ForumReplySerializer(reply).data, status=status.HTTP_201_CREATED)
