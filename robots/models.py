from customers.models import models
from django.utils import timezone


class Robot(models.Model):
    serial = models.CharField(max_length=5, blank=True, null=True)
    model = models.CharField(max_length=2, blank=False, null=False)
    version = models.CharField(max_length=2, blank=False, null=False)
    created = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        # If serial is not specified, then generate it according to the principle
        if not self.serial:
            count = Robot.objects.filter(model=self.model).count()
            count += 1
            # Convert to string with leading zeros
            count = str(count).zfill(3)
            self.serial = self.model + count
        
        if not self.created: # If the creation date is not specified
            self.created = timezone.now()
        # Call a method of the parent class
        super().save(*args, **kwargs)
    
    class Meta:
        db_table = 'robots'
