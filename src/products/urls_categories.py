from django.conf.urls import include, url

from .views import CategoryDetailView, CategoryListView


urlpatterns = [
    url(r'^$', CategoryListView.as_view(), name="list"),
    url(r'^(?P<slug>[\w-]+)/$', CategoryDetailView.as_view(), name="detail"),
]