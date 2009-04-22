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
        
    def is_metric(self):
        if self.subdivision == 'metric':
            return True
        return False

    def is_dimension(self):
        if self.subdivision == 'dimension':
            return True
        return False

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
        
    def is_time_key(self, ex=''):
        if self.name == ex:
            return False
        if self.name in ['ga:hour', 'ga:date', 'ga:day', 'ga:month', 'ga:week', 'ga:year']:
            return True
        else:
            return False
        
    def compatable_with(self, other, reverse=False):
        """
        Tests compatability with other dimension categories
        All dimensions are compatible with everything in their own category
        
        This is an implementation of the complicated flowchart at:
        http://code.google.com/apis/analytics/docs/gdata/gdataReferenceDimensionsMetrics.html#validCombinations
        """
    
        if other.category == self.category:
            return True
        # if self.category.compatability.filter(id=field_type.category.id).count() >= 1:
        #     return True
        # else:
        #     return False
        # elif (self.category.is_metric() and self.category.name == 'campaign') or self.name in ['ga:adContent', 'ga:adSlot', 'ga:adSlotPosition']:
        #     if (other.category.is_dimension()
        #         and other.category.name == 'campaign' 
        #         or other.is_time_key(ex='ga:hour')):
        #         
        #         return True
        #     elif (other.category.is_metric()
        #         and other.name not in ['ga:visitors',]):
        #         
        #         return True
        #         
        #     return False
        if self.category.is_dimension() and self.category.name == 'content':
            if (other.category.is_dimension()
                and other.category.name == 'content' 
                or other.is_time_key(ex='ga:hour')):
                
                return True
            elif (other.category.is_metric()
                and other.category.name != 'campaign'
                and other.name not in ['ga:visitors']):
                
                return True
            
            return False
            
        elif other.category.is_dimension() and other.category.name == 'content':
            if (self.category.is_dimension()
                and self.category.name == 'content' 
                or self.is_time_key(ex='ga:hour')):

                return True
            elif (self.category.is_metric()
                and self.category.name != 'campaign'
                and self.name not in ['ga:visitors']):

                return True

            return False
            
        elif self.name in ['ga:visitors',]:
            if other.is_time_key(ex='ga:hour'):
                
                return True
                
            elif (other.category.is_metric()
                and other.category.name == 'visitor'):
                
                return True
                
            return False
            
        elif other.name in ['ga:visitors',]:
            if self.is_time_key(ex='ga:hour'):
                
                return True
                
            elif (self.category.is_metric()
                and self.category.name == 'visitor'):
                
                return True
                
            return False
            
        else:

            if (other.category.is_dimension()
                and other.category.name != 'content' 
                and other.name not in ['ga:adContent', 'ga:adSlot', 'ga:adSlotPosition']):
                pass
            elif (other.category.is_metric()):
                pass
            else:
                return False
                
            if (self.category.is_dimension()
                and self.category.name != 'content' 
                and self.name not in ['ga:adContent', 'ga:adSlot', 'ga:adSlotPosition']):
                pass
            elif (self.category.is_metric()):
                pass
            else:
                return False
                
            return True
            