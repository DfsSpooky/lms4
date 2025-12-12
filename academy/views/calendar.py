from django.shortcuts import get_object_or_404
from django.views import View
from django.http import HttpResponse
from ..models import Ticket
from django.contrib.auth.mixins import LoginRequiredMixin

class DownloadICSView(LoginRequiredMixin, View):
    def get(self, request, ticket_id):
        ticket = get_object_or_404(Ticket, id=ticket_id, user=request.user)
        event = ticket.event

        # Simple ICS generation without external lib dependency
        start = event.start_date.strftime('%Y%m%dT%H%M00Z')
        end = event.end_date.strftime('%Y%m%dT%H%M00Z')
        now = event.created_at.strftime('%Y%m%dT%H%M00Z')

        ics_content = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//LMS Academy//Events//EN
BEGIN:VEVENT
UID:{ticket.id}@lmsacademy.com
DTSTAMP:{now}
DTSTART:{start}
DTEND:{end}
SUMMARY:{event.title}
DESCRIPTION:{event.description}
LOCATION:{event.location}
END:VEVENT
END:VCALENDAR"""

        response = HttpResponse(ics_content, content_type='text/calendar')
        response['Content-Disposition'] = f'attachment; filename="event_{event.id}.ics"'
        return response
