from functools import update_wrapper
from django.utils.translation import ugettext as _, ugettext_lazy
from django.contrib import admin

class AdminSiteWrapper(object):
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

    def _set_static(self):
        # Text to put at the end of each page's <title>.
        #self._instance.site_title = ugettext_lazy('Django Advanced Site Admin')

        # Text to put in each page's <h1>.
        self._instance.site_header = _('Advanced Django Administration')

        # Text to put at the top of the admin index page.
        #self._instance.index_title = ugettext_lazy('Advanced Site Administration')

        ## URL for the "View site" link at the top of each admin page.
        #self._instance.site_url = '/'

        #self._instance.login_form = None
        #self._instance.index_template = None
        #self._instance.app_index_template = None
        #self._instance.login_template = None
        #self._instance.logout_template = None
        #self._instance.password_change_template = None
        #self._instance.password_change_done_template = None

    def register_app_index_extra(self, app_label, func_dict_return):
        self._app_index_register.update({ app_label: func_dict_return, })

    def register_index_extra(self, func_dict_return):
        self._index_register.append(func_dict_return)

    def register_notification(self, model, msg_callback):
        """ MISSING """
        self._notification_callbacks.update(
            { model: msg_callback }
        )

    def __init__(self, instance, **kwargs):
        self._instance = instance
        self._app_index_register = {}
        self._index_register = []
        self._notification_callbacks = {}
        self._set_static()

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

    def index(self, request, extra_context=None):
        if not extra_context:
            extra_context={}
        for e in self._index_register:
            extra_context.update(e(request))
        extra_context['notifications'] = self._mk_notifications(request)
        return self._instance.index(request, extra_context)

    def app_index(self, request, app_label, extra_context=None):
        if not extra_context:
            extra_context={}
        if app_label in self._app_index_register.keys():
            extra_context.update(self._app_index_register[app_label](request))
        return self._instance.app_index(request, app_label, extra_context)

    def get_urls(self):
        from django.conf.urls import url, include
        # Since this module gets imported in the application's root package,
        # it cannot import models from other applications at the module level,
        # and django.contrib.contenttypes.views imports ContentType.
        from django.contrib.contenttypes import views as contenttype_views

        def wrap(view, cacheable=False):
            def wrapper(*args, **kwargs):
                return self.admin_view(view, cacheable)(*args, **kwargs)
            wrapper.admin_site = self
            return update_wrapper(wrapper, view)

        # Admin-site-wide views.
        urlpatterns = [
            url(r'^$', wrap(self.index), name='index'),
            url(r'^login/$', self.login, name='login'),
            url(r'^logout/$', wrap(self.logout), name='logout'),
            url(r'^password_change/$', wrap(self.password_change, cacheable=True), name='password_change'),
            url(r'^password_change/done/$', wrap(self.password_change_done, cacheable=True),
                name='password_change_done'),
            url(r'^jsi18n/$', wrap(self.i18n_javascript, cacheable=True), name='jsi18n'),
            url(r'^r/(?P<content_type_id>\d+)/(?P<object_id>.+)/$', wrap(contenttype_views.shortcut),
                name='view_on_site'),
        ]

        # Add in each model's views, and create a list of valid URLS for the
        # app_index
        valid_app_labels = []
        for model, model_admin in self._registry.items():
            urlpatterns += [
                url(r'^%s/%s/' % (model._meta.app_label, model._meta.model_name), include(model_admin.urls)),
            ]
            if model._meta.app_label not in valid_app_labels:
                valid_app_labels.append(model._meta.app_label)

        # If there were ModelAdmins registered, we should have a list of app
        # labels for which we need to allow access to the app_index view,
        if valid_app_labels:
            regex = r'^(?P<app_label>' + '|'.join(valid_app_labels) + ')/$'
            urlpatterns += [
                url(regex, wrap(self.app_index), name='app_list'),
            ]
        return urlpatterns

    @property
    def urls(self):
        return self.get_urls(), 'admin', self.name

default_admin_site = admin.site
admin_site = AdvancedAdminSite(default_admin_site)

