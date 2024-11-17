from django.urls import path
from .views import portfolio_allocation
from .views import dashboard_allocation

urlpatterns = [
    path('allocation/', portfolio_allocation, name='portfolio_allocation'),
    path('dashboard/', dashboard_allocation, name='stock_dashboard'),  

]
