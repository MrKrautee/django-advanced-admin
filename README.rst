=====================
Django Advanced Admin   
=====================

Adds extra context to ``admin:index`` and ``admin:app_index``. 
You can still use the 'normal' admin site
for registering models. So there is no need to change admin.py for existing apps.

It fowards all calls to the 'normal' admin.site if it self has no matching
attribute or method (__getattr__).

Version: very alpha

Features
========

* add context to ``app_index_view``, each app can add its own context.
* add context to ``index_view``
* add notifications to ``index_view``
    
Installation
============

Add ``advanced_admin`` to ``INSTALLED_APPS`` in your projects ``settings.py``.
Be sure you place it before ``django.contrib.admin``. Otherwise the custom
``index.html`` template, used for the notifications will not be loaded.

::

    # my_project/my_project/settings.py
    .
    .
    .
    INSTALLED_APPS = [
        # ... other apps 
        'advanced_admin.apps.AdvancedAdminConfig',#!!!place it before admin
        # ... more apps 
        'django.contrib.admin',
        # ... so much more apps 
    ]

Instead of 'normal' AdminSite import advanced admin in ``urls.py``.
Use it like 'normal' admin.site:

::

    # /my/project/project/urls.py

    from django.conf.urls import url
    form advanced_admin.admin import admin_site
    
    urlpatterns = [
        url(r'^admin/', admin_site.urls),
    ]
    
No need to register any ModelAdmin to ``advanced_admin.admin_site``.
You can still use the normal ``admin.site`` to register your ModelAdmin:

::

    from django.contrib.admin import site
    site.register(MyModel, MyModelAdmin)

Usage
=====    

Register additional content for index_view
------------------------------------------

With ``register_index_extra(extra_context_callback)`` you can register some
extra context in your admin.py. ``extra_context_callback`` gets the request
object and has to return a dict with the desired extra context to be used in the
``admin/index.html`` template.
Could look like this:

::

    # /my/project/mypp/admin.py

    from advanced_admin import admin_site
    
    def additional_index_content(request):
        
        return {
                'bla': 'blub',
                'my': 'extra',
                'ex': 'ample',
        }
    admin_site.register_index_extra(additional_index_content)
    
    
Register additional content for app_index_view
----------------------------------------------

``register_app_index_extra(app_label, extra_context_callback)``: Same here, but 
needs the app_label. Extra context can be used in the ``admin/app_index.html``.
Example:

::

    # /my/project/myapp/admin.py
    
    from advanced_admin import admin_site
    from app_settings.models import AppSetting

    def app_index(request):
        color = AppSetting.get_setting("myapp", "preferred_index_color")
        return { 
            'index_color': color,
            'extra': 'extra content bka bkub', 
        }
    
    admin_site.register_app_index_extra('myapp', app_index)


Register notifications in index_view
---------------------------------

Use ``reqister_notification(MyModel, message_callback)`` to register
notifications for the index view.

``message_callback`` has to accept an request objects as parameter and
has to return a dict. If you use the the delivered notifications
template the return dict must have 'msg' and 'url' as keys:

::

    # /my/project/my_app/admin.py

    from advanced_admin import admin_site

    def waether_msg_callback(request):
        msg = "no sun today"
        if weather.is_sunny():
            msg = "sunny day"
        return { 'msg': msg, 'url': '/admin/weather/forecast'}

    admin_site.register_notification(Weather, weather_msg_callback)

I use it to show up notifications in admin index 
for each new Comment in my blog app:

::

    # /my/project/blog/admin.py
    
    from advanced_admin import admin_site
    
    def msg_new_comment(request):
        comments_qs = Comment.objects.get_unapproved()
        comments_count = comments_qs.count()
        msg = _('%i new comment(s) to approve.') % comments_count
        app_label = Comment._meta.app_label
        model_name = Comment._meta.model_name
        url = reverse('admin:%s_%s_changelist' % (app_label, model_name))
        url = '%s?is_active__exact=0' % url
        if comments_count > 0:
            return {'msg': msg, 'url': url}
        return None
    admin_site.register_notification(Comment, msg_new_comment)
    
Access registered context 
-------------------------

The extra context variables you add here, can be accessed 
in the views templates. They are located in ``../django/contrib/admin/templates/admin/``

* index_view: ``index.html``
* app_index_view: ``app_index.html``

Access Notifications 
--------------------

For notifications there is an default template in this porject.
See ``django-advanced-admin/advanced_admin/templates/admin/index.html``
