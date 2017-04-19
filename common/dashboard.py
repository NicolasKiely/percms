from .core import render
from django.core.urlresolvers import reverse


class App_Dashboard(object):
    ''' Dashboard manager for app '''
    def __init__(self):
        self.name = ''
        self.namespace = ''


class Model_Dashboard(object):
    ''' Dashboard manager for models '''
    def __init__(self, app, model):
        self.app = app
        self.name = ''
        self.namespace = ''
        self.model = model
        self.listing_headers = []
        

    def get_listing_record(self, x):
        return (str(x),)

    def get_listing_panel(self, panel_title, **filters):
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

    def render_model_set(self, request, context):
        context['title'] = self.name + ' Manager'
        context['model_name'] = self.name
        context['app_dashboard'] = reverse(self.app.namespace+':dashboard')
        context['form'] = {
            'action': self.app.namespace +':add_'+ self.namespace,
            'fields': self.model().to_form_fields()
        }
        return render(request, 'common/model_set_editor.html', **context)
