from common.dashboard import App_Dashboard, Model_Dashboard, dashboard_view_closure
from .models import Script, Source, Log_Message
from . import script_views


# App dashboard
Dashboard = App_Dashboard()
Dashboard.name = 'Scripting'
Dashboard.namespace = 'script'


# Script dashboard
Script_Dashboard = Model_Dashboard(Dashboard, Script)
Script_Dashboard.name = 'Script'
Script_Dashboard.namespace = 'script'
Script_Dashboard.listing_headers = ['Category', 'Name']
Script_Dashboard.get_listing_record = \
    lambda x: [x.category, x.name]

Script_Dashboard.view_editor = dashboard_view_closure(
    Script_Dashboard, script_views.editor
)

Script_Dashboard.view_public = dashboard_view_closure(
    Script_Dashboard, script_views.view_public
)

Script_Dashboard.model_editor_template = 'scripting/editor.html'


# Source dashboard
Source_Dashboard = Model_Dashboard(Dashboard, Source)
Source_Dashboard.name = 'Source'
Source_Dashboard.namespace = 'source'
Source_Dashboard.model_editor_template = 'scripting/editor.html'
Source_Dashboard.view_editor = dashboard_view_closure(
    Source_Dashboard, script_views.source_editor
)
Source_Dashboard.post_edit = dashboard_view_closure(
    Source_Dashboard, script_views.edit_source
)
Source_Dashboard.post_delete = dashboard_view_closure(
    Source_Dashboard, script_views.delete_source
)


# Logging dashboard
Log_Dashboard = Model_Dashboard(Dashboard, Log_Message)
Log_Dashboard.name = 'Logging'
Log_Dashboard.namespace = 'logging'
Log_Dashboard.listing_headers = ['Message']
Log_Dashboard.get_listing_record = \
    lambda x: [str(x)]
