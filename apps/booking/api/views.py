from django.shortcuts import render

# other imports
from .decorators import has_permission


@has_permission('retrive_job')
def job_list(request):
    # ...
    pass


@has_permission('update_project')
def project_edit(request):
    # ...
    pass
