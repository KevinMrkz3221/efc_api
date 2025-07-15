# core/dashboard.py
from jet.dashboard.dashboard import Dashboard
from jet.dashboard.modules import DashboardModule

class ChartModule(DashboardModule):
    title = 'Mi Gráfico'
    template = 'admin/dashboard_admin.html'  # Este template lo crearás más adelante
    collapsible = False

    def init_with_context(self, context):
        self.children = []

class CustomIndexDashboard(Dashboard):
    columns = 2

    def init_with_context(self, context):
        self.children.append(ChartModule())
