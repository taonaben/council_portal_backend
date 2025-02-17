from django.urls import path
import portal.features.taxes.tax_views as views

urlpatterns = [
    path('all/', views.tax_list.as_view(), name='tax_list'),
    path('<uuid:tax_id>/', views.tax_detail.as_view(), name='tax_detail'),
    path('tax_payers/<uuid:city_id>/', views.tax_payer_list.as_view(), name='tax_payer_list'),
    path('tax_payers/<uuid:city_id>/<int:tax_payer_id>/', views.tax_payer_detail.as_view(), name='tax_payer_detail'),
    path('tax_exemptions/', views.tax_exemption_list.as_view(), name='tax_exemption_list'),
    path('tax_exemptions/<uuid:tax_exemption_id>/', views.tax_exemption_detail.as_view(), name='tax_exemption_detail'),
    path('tax_bills/', views.tax_bill_list.as_view(), name='tax_bill_list'),
    path('tax_bills/<uuid:tax_bill_id>/', views.tax_bill_detail.as_view(), name='tax_bill_detail'),
]