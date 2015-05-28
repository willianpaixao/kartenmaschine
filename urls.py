from django.conf.urls import patterns, include, url

from views import *

urlpatterns = patterns('',

    url(r'box/(?P<pk>\d+)/export/$', BoxExportView.as_view(), name="box_export"),
    url(r'sec/(?P<pk>\d+)/export/$', SectionExportView.as_view(), name="sec_export"),
    url(r'sub/(?P<pk>\d+)/export/$', SubsectionExportView.as_view(), name="sub_export"),
    url(r'card/(?P<pk>\d+)/export/$', CardExportView.as_view(), name="card_export"),
#    url(r'card/(?P<pk>\d+)/export/$', ExportFormView.as_view(), name="export"),
)
