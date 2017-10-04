from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404

@login_required
def view_public(request, dashboard, pk):
    obj = get_object_or_404(dashboard.model, pk=pk)
    context = {
        'panels': [
            {
                'title': 'Message',
                'pre': obj.long_message
            }
        ]
    }
    return dashboard.view_model(request, obj, context)
