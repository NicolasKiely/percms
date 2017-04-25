from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.conf.urls import url
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from .core import render


def dashboard_view_closure(dashboard, func):
    ''' Closure for binding dashboard to view functions (2nd arg) '''
    d=dashboard
    def inner_func(request, **kwargs):
        return func(request, d, **kwargs)

    return inner_func


def dashboard_sublist_view_closure(dashboard, func, field):
    ''' Closure for binding dashboard and sublist criteria '''
    d=dashboard
    f=field
    def inner_func(request, **kwargs):
        return func(request, d, f, **kwargs)

    return inner_func



def default_view_app_dashboard(request, dashboard):
    context = {
        'panels': [
            d.get_dashboard_panel()
            for d in dashboard.children
            if d.show_on_app_dashboard
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
def default_view_model_sublist(request, dashboard, field, fk):
    ''' Default handler for viewing subsets of objects '''
    parent = dashboard.get_parent(field)
    parent_obj = get_object_or_404(parent.model, pk=fk)
    context = {
        'model_dashboard': dashboard.link_dashboard(),
        'nav': dashboard.edit_link(parent_obj),
        'title': '%s Listing for %s: %s' % (dashboard.name, parent.name, str(parent_obj)),
        'panels': [
            dashboard.get_sublisting_panel(dashboard.name +'s', '')
        ]
    }
    return dashboard.render_model_set(request, context, field, fk)


@login_required
def default_view_model(request, dashboard, pk):
    ''' Default handler for viewing object '''
    obj = get_object_or_404(dashboard.model, pk=pk)
    return dashboard.view_model(request, obj, {})


@login_required
def default_view_model_editor(request, dashboard, pk):
    ''' Default handler for viewing object editor '''
    obj = get_object_or_404(dashboard.model, pk=pk)
    context = {
        'model_dashboard': dashboard.link_dashboard(),
        'panels':[
            child.get_sublisting_panel(
                child.name +' Listing', 
                child.reverse_sublist(dashboard, pk)
            )
            for child in dashboard.children
        ]
    }
    return dashboard.render_model(request, obj, context)


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
        self.children = []
        self.view_dashboard = dashboard_view_closure(self, default_view_model_dashboard)
        self.view_public = dashboard_view_closure(self, default_view_model)
        self.view_editor = dashboard_view_closure(self, default_view_model_editor)
        self.view_sublist = default_view_model_sublist
        self.post_add = dashboard_view_closure(self, default_post_model_add)
        self.post_edit = dashboard_view_closure(self, default_post_model_edit)
        self.post_delete = dashboard_view_closure(self, default_post_model_delete)
        self.model_set_editor_template = 'common/model_set_editor.html'
        self.model_editor_template = 'common/model_editor.html'
        self.model_view_template = 'common/model_view.html'
        app.children.append(self)
        self.show_on_app_dashboard = True
        self.parents = {}

    def child_of(self, parent, field):
        ''' Make model child of other dashboard '''
        parent.children.append(self)
        self.parents[field] = parent

    def get_parent(self, field):
        return self.parents[field]

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
        return [str(x)]

    def get_listing_panel(self, panel_title, **filters):
        ''' Panel listing structure '''
        return {
            'title': panel_title,
            'table': {
                'headers': self.listing_headers + ['URL'],
                'rows': [
                    self.get_listing_record(x) +
                    [self.edit_link(x) +' | '+ self.view_link(x),]
                    for x in self.model.objects.filter(**filters)[:5]
                ]
            }
        }

    def get_sublisting_panel(self, panel_title, title_link, **filters):
        ''' Panel listing as child '''
        return {
            'title': self.name +' Listing',
            'link': title_link,
            'table': {
                'headers': self.listing_headers + ['URL'],
                'rows': [
                    self.get_listing_record(x) +
                    [self.edit_link(x) +' | '+ self.view_link(x),]
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
                'headers': self.listing_headers + ['URL'],
                'rows': [
                    self.get_listing_record(x) +
                    [self.edit_link(x) +' | '+ self.view_link(x)]
                    for x in self.model.objects.filter(**filters)[:5]
                ]
            }
        }

    def render_model_set(self, request, context, field=None, fk=None):
        ''' Model set manager page '''
        context['title'] = context.get('title', self.name + ' Manager')
        context['model_name'] = self.name
        context['app_dashboard'] = self.app.reverse_dashboard()
        if field is None:
            form_fields = self.model().to_form_fields()
        else:
            form_fields = self.model().to_form_fields(field, fk)

        context['form'] = {
            'action': self.app.namespace +':add_'+ self.namespace,
            'fields': form_fields
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

    def url_view_sublist(self, route, field):
        ''' URL for sublist view '''
        return url(
            route, dashboard_sublist_view_closure(self, self.view_sublist, field),
            name='sublist_%s_%s' % (self.namespace, field)
        )

    def url_post_add(self, route):
        ''' URL for add '''
        return url(route, self.post_add, name='add_'+self.namespace)

    def url_post_edit(self, route):
        ''' URL for edit '''
        return url(route, self.post_edit, name='edit_'+self.namespace)

    def url_post_delete(self, route):
        ''' URL for delete '''
        return url(route, self.post_delete, name='delete_'+self.namespace)

    def create_standard_urls(self):
        url = '^'+ self.namespace +'/%s$'
        sublist_urls = [
            self.url_view_sublist(
                r'^%s/sublist-%s/%s$' % (self.namespace, k, '(?P<fk>\d)/[\w\.]*'),
                k
            )
            for k,v in self.parents.iteritems()
        ]
        return [
            self.url_view_dashboard(url % 'dashboard/'),
            self.url_view_editor(url % 'editor/(?P<pk>\d+)/[\w\.]*'),
            self.url_view_public(url % 'view/(?P<pk>\d+)/[\w\.]*'),
            self.url_post_add(url % 'add/'),
            self.url_post_edit(url % 'edit/'),
            self.url_post_delete(url % 'delete/')
        ] + sublist_urls

    def reverse_dashboard(self):
        ''' Reverse URL lookup for model set manager '''
        return reverse(self.app.namespace+':'+self.namespace+'_dashboard')

    def reverse_editor(self, *args):
        return reverse(self.app.namespace+':'+self.namespace+'_editor', args=args)

    def reverse_view(self, *args):
        return reverse(self.app.namespace+':'+self.namespace+'_view', args=args)

    def reverse_delete(self):
        ''' Reverse URL lookup for delete model post '''
        return reverse(self.app.namespace+':delete_'+self.namespace)

    def reverse_sublist(self, parent, value):
        ''' Reverse URL lookup for filtering listing by parent model '''
        parent_field = [k for k,v in self.parents.iteritems() if v==parent][0]
        return reverse(
            '%s:sublist_%s_%s' % (self.app.namespace, self.namespace, parent_field),
            args=(value,)
        )

    def link_dashboard(self):
        return '<a href="%s">%s Manager</a>' % (self.reverse_dashboard(), self.name)

    def edit_link(self, obj):
        return '<a href="%s">Edit %s</a>' % (self.reverse_editor(obj.id), self.name)

    def view_link(self, obj):
        return '<a href="%s">View %s</a>' % (self.reverse_view(obj.id), self.name)
