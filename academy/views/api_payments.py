from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from ..models import Installment, Enrollment
from ..serializers import InstallmentSerializer

class InstallmentViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = InstallmentSerializer

    def get_queryset(self):
        # Return installments for the current user's enrollments
        return Installment.objects.filter(enrollment__user=self.request.user)

    @action(detail=True, methods=['post'])
    def upload_voucher(self, request, pk=None):
        installment = self.get_object()

        if 'voucher' not in request.FILES:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        installment.voucher_image = request.FILES['voucher']
        installment.status = 'review'
        installment.save()

        return Response({'status': 'uploaded'})
