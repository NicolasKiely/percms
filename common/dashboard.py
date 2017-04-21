from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.conf.urls import url
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from .core import render



def dashboard_view_closure(dashboard, func):
    d=dashboard
    def inner_func(request, **kwargs):
        return func(request, d, **kwargs)

    return inner_func


def default_view_app_dashboard(request, dashboard):
    context = {
        'panels': [
            d.get_dashboard_panel()
            for d in dashboard.children
        ]
    }
    return dashboard.render(request, context)


class App_Dashboard(object):
    ''' Dashboard manager for app '''
    def __init__(self):
        self.name = ''
        self.namespace = ''
        self.view_dashboard = dashboard_view_closure(self, default_view_app_dashboard)
        self.children = []

    def render(self, request, context):
        context['title'] = self.name +' Dashboard'
        context['app'] = self.name
        return render(request, 'common/app_dashboard.html', **context)

    def reverse_dashboard(self):
        return reverse(self.namespace+':dashboard')

    def url_view_dashboard(self, route):
        ''' URL for dashboard '''
        return url(route, self.view_dashboard, name='dashboard')


@login_required
def default_view_model_dashboard(request, dashboard):
    context = {
        'panels': [
            dashboard.get_listing_panel(dashboard.name+'s')
        ]
    }
    return dashboard.render_model_set(request, context)


@login_required
def default_view_model(request, dashboard, pk):
    ''' Default handler for viewing object '''
    obj = get_object_or_404(dashboard.model, pk=pk)
    return dashboard.view_model(request, obj, {})


@login_required
def default_view_model_editor(request, dashboard, pk):
    ''' Default handler for viewing object editor '''
    obj = get_object_or_404(dashboard.model, pk=pk)
    return dashboard.render_model(request, obj, {})


@login_required
def default_post_model_add(request, dashboard):
    ''' Default handler for adding an object '''
    obj = dashboard.model_from_post(request.POST)
    obj.save()
    return HttpResponseRedirect(dashboard.reverse_dashboard())


@login_required
def default_post_model_edit(request, dashboard):
    ''' Default handler for editting an object '''
    obj = get_object_or_404(dashboard.model, pk=request.POST['pk'])
    dashboard.edit_object_from_post(obj, request.POST)
    obj.save()
    return HttpResponseRedirect(dashboard.reverse_dashboard())

@login_required
def default_post_model_delete(request, dashboard):
    ''' Default handler for deleting object '''
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
        self.view_public = dashboard_view_closure(self, default_view_model)
        self.view_editor = dashboard_view_closure(self, default_view_model_editor)
        self.post_add = dashboard_view_closure(self, default_post_model_add)
        self.post_edit = dashboard_view_closure(self, default_post_model_edit)
        self.post_delete = dashboard_view_closure(self, default_post_model_delete)
        self.model_set_editor_template = 'common/model_set_editor.html'
        self.model_editor_template = 'common/model_editor.html'
        self.model_view_template = 'common/model_view.html'
        app.children.append(self)

    def model_from_post(self, POST):
        ''' Create new model instance from POST variables '''
        fields = {}
        for key, val in POST.iteritems():
            if key=='csrfmiddlewaretoken' or key=='pk':
                continue
            else:
                fields[key] = val
        return self.model(**fields)

    def edit_object_from_post(self, obj, POST):
        ''' Edits object given POST variables '''
        fields = {}
        dict_obj = obj.__dict__
        for key, val in POST.iteritems():
            if key=='csrfmiddlewaretoken' or key=='pk':
                continue
            else:
                dict_obj[key] = val

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
        return render(request, self.model_set_editor_template, **context)

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
        return render(request, self.model_editor_template, **context)

    def view_model(self, request, obj, context):
        ''' Public view of object '''
        context['title'] = self.name + ' View'
        context['name'] = str(obj)
        context['model'] = self.name
        return render(request, self.model_view_template, **context)

    def url_view_dashboard(self, route):
        ''' URL for dashboard '''
        return url(route, self.view_dashboard, name=self.namespace+'_dashboard')

    def url_view_public(self, route):
        ''' URL for general view '''
        return url(route, self.view_public, name=self.namespace+'_view')

    def url_view_editor(self, route):
        ''' URL for editor '''
        return url(route, self.view_editor, name=self.namespace+'_editor')

    def url_post_add(self, route):
        ''' URL for add '''
        return url(route, self.post_add, name='add_'+self.namespace)

    def url_post_edit(self, route):
        ''' URL for edit '''
        return url(route, self.post_edit, name='edit_'+self.namespace)

    def url_post_delete(self, route):
        ''' URL for delete '''
        return url(route, self.post_delete, name='delete_'+self.namespace)

    def reverse_dashboard(self):
        ''' Reverse URL lookup for model set manager '''
        return reverse(self.app.namespace+':'+self.namespace+'_dashboard')

    def reverse_delete(self):
        ''' Reverse URL lookup for delete model post '''
        return reverse(self.app.namespace+':delete_'+self.namespace)
