"""callculator URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from rest_framework.documentation import include_docs_urls

from .records.views import RecordCall, CallDetails, Bills

urlpatterns = [
    path('records/', RecordCall.as_view()),
    path('records/<call_id>/', CallDetails.as_view()),
    path('bills/<phone>/', Bills.as_view()),
    path('bills/<phone>/<month_year>/', Bills.as_view()),
    path('docs/', include_docs_urls(title='Calls Records API')),
    path('admin/', admin.site.urls),
]
