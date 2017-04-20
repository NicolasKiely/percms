from common.dashboard import App_Dashboard, Model_Dashboard, dashboard_view_closure
from .models import Script, Source
from .script_views import editor


# App dashboard
Dashboard = App_Dashboard()
Dashboard.name = 'Scripting'
Dashboard.namespace = 'script'


# Script dashboard
Script_Dashboard = Model_Dashboard(Dashboard, Script)
Script_Dashboard.name = 'Script'
Script_Dashboard.namespace = 'script'
Script_Dashboard.listing_headers = ['Category', 'Name', 'URL']
Script_Dashboard.get_listing_record = \
    lambda x: (x.category, x.name)

Script_Dashboard.view_editor = dashboard_view_closure(
    Script_Dashboard, editor
)

Script_Dashboard.model_editor_template = 'scripting/editor.html'
