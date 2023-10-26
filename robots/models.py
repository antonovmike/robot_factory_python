from django.db import models


class Robot(models.Model):
    # serial = models.CharField(max_length=5, blank=False, null=False)
    serial = models.CharField(max_length=5, blank=True, null=True)
    model = models.CharField(max_length=2, blank=False, null=False)
    version = models.CharField(max_length=2, blank=False, null=False)
    created = models.DateTimeField(blank=False, null=False)

    def save(self, *args, **kwargs):
        # Если serial не задан, то сгенерировать его по принципу
        if not self.serial:
            # Получить количество роботов с такой же моделью
            count = Robot.objects.filter(model=self.model).count()
            count += 1
            # Преобразовать в строку с лидирующими нулями
            count = str(count).zfill(3)
            # Сконкатенировать с моделью
            self.serial = self.model + count
            # Вызвать метод родительского класса
        super().save(*args, **kwargs)


class Customer(models.Model):
    name = models.TextField(blank=False, null=False)
    email = models.EmailField(blank=False, null=False, unique=True)
    login = models.TextField(blank=False, null=False, unique=True)
    password = models.TextField(blank=False, null=False)

    class Meta:
        db_table = 'customers'


class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    robot = models.ForeignKey(Robot, on_delete=models.CASCADE)
    order_date = models.DateTimeField(blank=False, null=False)

    class Meta:
        db_table = 'orders'
