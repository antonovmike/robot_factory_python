from .models import Robot
from django.core.serializers import Serializer
import json

class RobotSerializer(Serializer):
    def serialize(self, queryset, **options):
        # Преобразование queryset в список словарей
        data = [
            {'model': item.model, 'version': item.version, 'created': item.created}
            for item in queryset
        ]
        # Преобразование списка словарей в JSON
        return json.dumps(data)

    def deserialize(self, stream_or_string, **options):
        # Преобразование JSON в список словарей
        data = json.loads(stream_or_string)
        # Создание объектов Robot на основе данных из списка словарей
        robots = [
            Robot(model=item['model'], version=item['version'], created=item['created'])
            for item in data
        ]
        return robots
