======================================
Django Advanced Admin - Version: alpha  
======================================

Adds funtionality to the 'normal' admin. BUt you can use the 'normal' admin
for registering models. So there is no need to change admin.py from
existing apps.
It fowards all calls to the 'normal' admin if it self has no matching
attribute or method (__getattr__).

Features
========

    * add context to app_index view, each app can add its own context.
    * add context to index_view
    * add notifications to index_view
    
Installation
============
    Instead of 'normal' AdminSite import advanced admin in urls.py.
    Use it like 'normal' admin.site:
    ::
        from django.conf.urls import url
        form advanced_admin.admin import admin_site
        urlpatterns = [
            url(r'^admin/', admin_site.urls),
        ]
        
    No need to register any ModelAdmin to advanced_admin.admin.admin_site.
    You can still use the normal admin.site to register your ModelAdmins:
    ::
        from django.contrib.admin import site
        site.register(MyModel, MyModelAdmin)

Usage
=====
importing advanced admin

::
    from advanced_admin import admin_site

    
Register additional content for index_view
------------------------------------------


Register additional content for app_index_view
----------------------------------------------


Register notifications index_view
---------------------------------
for example we have BlogEntries with Comments. We want to 
show up an notification in admin index for each new Comment.

::
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
