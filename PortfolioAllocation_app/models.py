from django.db import models

class Asset(models.Model):
    name = models.CharField(max_length=255, unique=True)
    symbol = models.CharField(max_length=10, unique=True)  # e.g., 'AAPL' for Apple

    def __str__(self):
        return self.name

class PortfolioAllocation(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    initial_capital = models.FloatField()
    risk_aversion = models.FloatField()
    weight = models.FloatField()  # Weight of the asset in the portfolio
    new_position = models.FloatField()  # New amount of the asset held
    new_weight = models.FloatField()  # New weight after allocation
    date_allocated = models.DateTimeField(auto_now_add=True)  # Record when the allocation was made

    def __str__(self):
        return f"{self.asset} Allocation on {self.date_allocated}"

    class Meta:
        verbose_name = "Portfolio Allocation"
        verbose_name_plural = "Portfolio Allocations"
        ordering = ['-date_allocated']  # Order by date descending
