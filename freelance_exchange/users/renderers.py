import json
from rest_framework.renderers import JSONRenderer


class UserJSONRenderer(JSONRenderer):
    charset = 'utf-8'

    def render(self, data, media_type=None, renderer_context=None):
        # Если мы получим ключ token как часть ответа, это будет байтовый
        # объект. Байтовые объекты плохо сериализуются, поэтому нам нужно
        # декодировать их перед рендерингом объекта User.
        token = data.get('token', None)

        if token is not None and isinstance(token, bytes):
            # Как говорится выше, декодирует token если он имеет тип bytes.
            data['token'] = token.decode('utf-8')

        # Наконец, мы можем отобразить наши данные в простанстве имен 'user'.
        return json.dumps({
            'user': data
        })
