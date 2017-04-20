from django.core.urlresolvers import reverse
from django.conf.urls import url
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from .core import render



def dashboard_view_closure(dashboard, func):
    d=dashboard
    def inner_func(request, **kwargs):
        return func(d, request, **kwargs)

    return inner_func


class App_Dashboard(object):
    ''' Dashboard manager for app '''
    def __init__(self):
        self.name = ''
        self.namespace = ''

    def render(self, request, context):
        context['title'] = self.name +' Dashboard'
        context['app'] = self.name
        return render(request, 'common/app_dashboard.html', **context)

    def reverse_dashboard(self):
        return reverse(self.namespace+':dashboard')


def default_view_model_dashboard(dashboard, request):
    context = {
        'panels': [
            dashboard.get_listing_panel(dashboard.name+'s')
        ]
    }
    return dashboard.render_model_set(request, context)


def default_view_model_editor(dashboard, request, pk):
    obj = get_object_or_404(dashboard.model, pk=pk)
    return dashboard.render_model(request, obj, {})


def default_post_model_delete(dashboard, request):
    obj = get_object_or_404(dashboard.model, pk=request.POST['pk'])
    obj.delete()
    return HttpResponseRedirect(dashboard.reverse_dashboard())


class Model_Dashboard(object):
    ''' Dashboard manager for models '''
    def __init__(self, app, model):
        self.app = app
        self.name = ''
        self.namespace = ''
        self.model = model
        self.listing_headers = []
        self.view_dashboard = dashboard_view_closure(self, default_view_model_dashboard)
        self.view_editor = dashboard_view_closure(self, default_view_model_editor)
        self.post_delete = dashboard_view_closure(self, default_post_model_delete)
        
    def get_listing_record(self, x):
        return (str(x),)

    def get_listing_panel(self, panel_title, **filters):
        ''' Panel listing structure '''
        return {
            'title': panel_title,
            'table': {
                'headers': self.listing_headers,
                'rows': [
                    self.get_listing_record(x) +
                    (x.edit_link() +' | '+ x.view_link(),)
                    for x in self.model.objects.filter(**filters)[:5]
                ]
            }
        }

    def get_dashboard_panel(self, **filters):
        ''' Panel structure for dashboard '''
        return {
            'title': self.name +' Management',
            'link': self.reverse_dashboard(),
            'table': {
                'headers': self.listing_headers,
                'rows': [
                    self.get_listing_record(x) +
                    (x.edit_link() +' | '+ x.view_link(),)
                    for x in self.model.objects.filter(**filters)[:5]
                ]
            }
        }

    def render_model_set(self, request, context):
        ''' Model set manager page '''
        context['title'] = self.name + ' Manager'
        context['model_name'] = self.name
        context['app_dashboard'] = self.app.reverse_dashboard()
        context['form'] = {
            'action': self.app.namespace +':add_'+ self.namespace,
            'fields': self.model().to_form_fields()
        }
        return render(request, 'common/model_set_editor.html', **context)

    def render_model(self, request, obj, context):
        ''' Model editor page '''
        context['title'] = self.name +' Editor'
        context['name'] = str(obj)
        context['model'] = self.name
        context['object'] = obj
        context['form'] = {
            'action': self.app.namespace +':edit_'+ self.namespace,
            'fields': obj.to_form_fields()
        }
        context['post_delete'] = self.reverse_delete()
        return render(request, 'common/model_editor.html', **context)

    def url_view_dashboard(self, route, view=None):
        ''' URL for dashboard '''
        view_func = self.view_dashboard if view is None else view
        return url(route, view_func, name=self.namespace+'_dashboard')

    def url_view_editor(self, route, view=None):
        ''' URL for editor '''
        view_func = self.view_editor if view is None else view
        return url(route, view_func, name=self.namespace+'_editor')

    def url_post_delete(self, route, view=None):
        ''' URL for delete '''
        view_func = self.post_delete if view is None else view
        return url(route, view_func, name='delete_'+self.namespace)

    def reverse_dashboard(self):
        ''' Reverse URL lookup for model set manager '''
        return reverse(self.app.namespace+':'+self.namespace+'_dashboard')

    def reverse_delete(self):
        ''' Reverse URL lookup for delete model post '''
        return reverse(self.app.namespace+':delete_'+self.namespace)
