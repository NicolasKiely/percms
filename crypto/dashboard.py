from common import dashboard as dbd
from . import models
from . import views

# App Dashboard
App_Dashboard = dbd.App_Dashboard()
App_Dashboard.name = 'Crypto Trading'
App_Dashboard.namespace = 'crypto'


# API key dashboard
Key_Dashboard = dbd.Model_Dashboard(App_Dashboard, models.API_Key)
Key_Dashboard.name = 'API Key'
Key_Dashboard.namespace = 'key'
Key_Dashboard.listing_headers = ['Name']
Key_Dashboard.get_listing_record = \
    lambda x: [x.name]

Key_Dashboard.post_add = dbd.dashboard_view_closure(
    Key_Dashboard, views.add_key
)

Key_Dashboard.post_edit = dbd.dashboard_view_closure(
    Key_Dashboard, views.edit_key
)


# Backtesting dashboard
BT_Dashboard = dbd.Model_Dashboard(App_Dashboard, models.Back_Test)
BT_Dashboard.name = 'Back Test'
BT_Dashboard.namespace = 'backtest'
BT_Dashboard.listing_headers = ['Script', 'Status']
BT_Dashboard.get_listing_record = \
    lambda x: [str(x.script), str(x.status)]

BT_Dashboard.post_add = dbd.dashboard_view_closure(
    BT_Dashboard, views.add_backtest
)

BT_Dashboard.model_view_template = 'crypto/backtest_view.html'
