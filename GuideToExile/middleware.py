import pytz

from django.utils import timezone


class TimezoneMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # storing timezone both in DB and session, taking from session first
        tzname = request.session.get('django_timezone')
        if not tzname and not request.user.is_anonymous:
            tzname = request.user.user_profile.timezone
        if tzname and tzname in pytz.common_timezones:
            timezone.activate(pytz.timezone(tzname))
        else:
            timezone.deactivate()
        return self.get_response(request)
