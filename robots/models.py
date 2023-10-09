from django.db import models


class Robot(models.Model):
    # serial = models.CharField(max_length=5, blank=False, null=False)
    serial = serial = models.CharField(max_length=5, blank=True, null=True)
    model = models.CharField(max_length=2, blank=False, null=False)
    version = models.CharField(max_length=2, blank=False, null=False)
    created = models.DateTimeField(blank=False, null=False)

    def save(self, *args, **kwargs):
        # Если serial не задан, то сгенерировать его по принципу
        if not self.serial:
            # Получить количество роботов с такой же моделью
            count = Robot.objects.filter(model=self.model).count()
            # Увеличить на единицу
            count += 1
            # Преобразовать в строку с лидирующими нулями
            count = str(count).zfill(3)
            # Сконкатенировать с моделью
            self.serial = self.model + count
            # Вызвать метод родительского класса
        super().save(*args, **kwargs)
