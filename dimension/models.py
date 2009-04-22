from django.db import models

# Create your models here.

class Category(models.Model):
    
    SUBDIVISION_CHOICES = (('dimension', 'dimension'), ('metric', 'metric'))
    
    name = models.CharField(null=False, max_length=20)
    subdivision = models.CharField(null=False, blank=False, default='dimension',
                                   choices=SUBDIVISION_CHOICES, max_length=20) #dimension or metric
    compatability = models.ManyToManyField("self", null=True, blank=True)
    
    unique_together = (("name", "subdivision"),)
    
    def __repr__(self):
        return self.name
        
    def __str__(self):
        return "%s: %s" % (self.subdivision, self.name)

class FieldType(models.Model):
    """
    Dimension or Metric
    """
    name = models.CharField(null=False, max_length=100)
    category = models.ForeignKey(Category)
    description = models.TextField(null=True)
    
    def __repr__(self):
        return self.name
        
    def __str__(self):
        return self.name
        
    def compatable_with(self, field_type):
        """
        Tests compatability with other dimension categories
        All dimensions are compatible with everything in their own category
        """
        if field_type.category == self.category:
            return True
        if self.category.compatability.filter(id=field_type.category.id).count() >= 1:
            return True
        else:
            return False