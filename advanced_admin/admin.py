from functools import update_wrapper
from django.utils.translation import ugettext as _, ugettext_lazy
from django.contrib import admin

class AdminSiteWrapper:
    """  MISSING """
    def __init__(self, instance):
        self._instance = instance

    def __getattr__(self, name):
        return self._instance.__getattribute__(name)


class AdvancedAdminSite(AdminSiteWrapper):
    """Adds funtionality to the 'normal' admin. BUt you can use the 'normal' admin
    for registering models. So there is no need to change admin.py from
    existing apps.

    It fowards all calls to the 'normal' admin if it self has no matching
    attribute or method (__getattr__).

    features:
        - add context to app_index view, each app can add its own context.
        - add context to index_view
        - add notifications to index_view

    Usage:
        Instead of 'normal' AdminSite import advanced admin in urls.py.
        Use it like 'normal' admin.site:
            from django.conf.urls import url
            form advanced_admin.admin import admin_site
            urlpatterns = [
                url(r'^admin/', admin_site.urls),
            ]
        No need to register any ModelAdmin to advanced_admin.admin.admin_site.
        You can still use the normal admin.site to register your ModelAdmins:
            from django.contrib.admin import site
            site.register(MyModel, MyModelAdmin)
    """

    def register_app_index_extra(self, app_label, func_dict_return):
        self._app_index_register.update({ app_label: func_dict_return, })

    def register_index_extra(self, func_dict_return):
        self._index_register.append(func_dict_return)

    def register_notification(self, model, msg_callback):
        """ register notifications for index view.
            msg_callback has to accept an request objects as parameter and
            has to return a dict. if you use the the delivered notifications
            template the return dict must have 'msg' and 'url' as keys.

            example:
                def msg_callback(request):
                    #... do something ....
                    msg = "no sun today"
                    if weather.is_sunny():
                        msg = "sunny day"
                    return { 'msg': msg, 'url': '/admin/weather/forecast'}
        """
        self._notification_callbacks.update(
            { model: msg_callback }
        )

    def __init__(self, instance, **kwargs):
        super().__init__(instance)
        self._app_index_register = {}
        self._index_register = []
        self._notification_callbacks = {}
        self._set_static()

    def _set_static(self):
        # Text to put at the end of each page's <title>.
        #self._instance.site_title = ugettext_lazy('Django Advanced Site Admin')

        # Text to put in each page's <h1>.
        self._instance.site_header = _('Advanced Django Administration')

        # Text to put at the top of the admin index page.
        #self._instance.index_title = ugettext_lazy('Advanced Site Administration')

    def _mk_notifications(self, request):
        """ return notifications as list of strings """
        msgs = []
        for model, callback in self._notification_callbacks.items():
            msg = callback(request)
            if msg:
                tmp = { 'app_label': model._meta.app_label,
                       'model_name': model._meta.model_name }
                tmp.update(msg)
                msgs.append(tmp)
        return msgs

    def _advanced_index(self, index_func):
        def wrap_index(request, extra_context=None):
            if not extra_context:
                extra_context={}
            for e in self._index_register:
                extra_context.update(e(request))
            extra_context['notifications'] = self._mk_notifications(request)
            return index_func(request, extra_context)
        return wrap_index

    def _advanced_app_index(self, app_index_func):
        def wrap_app_index(request, app_label, extra_context=None):
            if not extra_context:
                extra_context={}
            if app_label in self._app_index_register.keys():
                extra_context.update(self._app_index_register[app_label](request))
            return app_index_func(request, app_label, extra_context)
        return wrap_app_index

    @property
    def urls(self):
        # replace admin_site methods to get the 
        # added context in default admin_site
        self._instance.app_index = self._advanced_app_index(self._instance.app_index)
        self._instance.index = self._advanced_index(self._instance.index)
        return self._instance.urls

default_admin_site = admin.site
admin_site = AdvancedAdminSite(default_admin_site)

