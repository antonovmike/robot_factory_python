from customers.models import Customer, models


class Robot(models.Model):
    serial = models.CharField(max_length=5, blank=True, null=True)
    model = models.CharField(max_length=2, blank=False, null=False)
    version = models.CharField(max_length=2, blank=False, null=False)
    created = models.DateTimeField(blank=False, null=False)

    def save(self, *args, **kwargs):
        # Если serial не задан, то сгенерировать его по принципу
        if not self.serial:
            count = Robot.objects.filter(model=self.model).count()
            count += 1
            # Преобразовать в строку с лидирующими нулями
            count = str(count).zfill(3)
            self.serial = self.model + count
        # Вызвать метод родительского класса
        super().save(*args, **kwargs)
