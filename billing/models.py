# Create your models here.

from django.conf import settings
from django.db import models

CURRENCY_CHOICES = (
    ("INR", "INR"),
    ("USD", "USD")
)


class GST(models.Model):
    """
    This model class store GST slab information
    """
    slab = models.FloatField()

    def __str__(self):
        return f"{self.slab} % Slab"


class Product(models.Model):
    """
    Base class store product information
    """
    name = models.CharField(max_length=100)
    price = models.FloatField()
    gst = models.ForeignKey(GST, on_delete=models.CASCADE)
    gst_include = models.BooleanField(default=True)
    slug = models.SlugField()
    description = models.TextField()
    discount = models.FloatField()
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='INR')

    def __str__(self):
        """
        return: product name
        """
        return self.name

    def total_price(self):
        if self.gst_include:
            return self.price
        return self.price + (self.price * self.gst.slab)/100


class ProductOrder(models.Model):
    """
    This model class store product information while ordering.
    Product price and gst slab can be update time to time.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    price = models.FloatField(blank=True)
    gst_slab = models.FloatField(blank=True)
    # gst_include = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username} oder {self.quantity} quantity of {self.product.name}"

    def get_gst(self):
        """
        1. Add GST:
            GST Amount = (Original Cost x GST%)/100
            Net Price = Original Cost + GST Amount
        2. Remove GST:
            GST Amount = Original Cost – [Original Cost x {100/(100+GST%)}]
            Net Price = Original Cost – GST Amount.
        """
        return self.price - (self.price * (100/(100 + self.gst_slab)))

    def get_net_amount(self):
        return self.price - self.get_gst()

    def get_total_gst(self):
        return self.quantity * self.get_gst()

    def get_total_net_amount(self):
        return self.quantity * self.get_net_amount()

    def get_total_product_price(self):
        return self.quantity * self.price

    def save(self, *args, **kwargs):
        self.gst_slab = self.product.gst.slab
        self.price = self.product.total_price()
        super(ProductOrder, self).save(*args, **kwargs)
