from django.urls import path

from elect_app1 import views1, views2, views3

urlpatterns = [
    path('get_overview_data', views2.get_overview_data),
    path('get_region', views2.get_region),
    path('get_elect_start', views2.get_elect_start),
    path('get_fracture_data', views2.get_fracture_data),
    path('get_result_data', views2.get_result_data),
    path('get_take_quantity', views2.get_take_quantity),
    path('get_send_pdf', views2.get_send_pdf),

    # ----------------------------------
    path('get_data_timing', views3.get_data_timing),
    path('get_electricity_target', views3.get_electricity_target),
    path('get_electricity_target_timing', views3.get_electricity_target_timing),
    # path('get_quantity_coefficient', views3.get_quantity_coefficient),
    # path('get_quantity_coefficient_timing', views3.get_quantity_coefficient_timing),
    path('get_clean_energy', views3.get_clean_energy),
    path('get_clean_energy_timing', views3.get_clean_energy_timing),
    path('get_region_target', views3.get_region_target),
    path('get_synthesize_target', views3.get_synthesize_target),

]
