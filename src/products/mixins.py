from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from django.http import Http404


class StaffRequiredMixin:

    @classmethod
    def as_view(self, *args, **kwargs):
        view = super(StaffRequiredMixin, self).as_view(*args, **kwargs)
        return login_required(view)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        if self.request.user.is_staff:
            return super(StaffRequiredMixin, self).dispatch(*args, **kwargs)
        else:
            raise Http404


class LoginRequiredMixin:

    @classmethod
    def as_view(self, *args, **kwargs):
        view = super(LoginRequiredMixin, self).as_view(*args, **kwargs)
        return login_required(view)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(*args, **kwargs)
