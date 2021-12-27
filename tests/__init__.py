import json

from rest_framework import status


class ActMixin:
    @staticmethod
    def act(url, client, data=None, method="post", status_code=status.HTTP_201_CREATED, json_content_type=True):
        client_method = getattr(client, method)
        if method in ("post", "patch", "put"):
            if json_content_type:
                response = client_method(url, data=json.dumps(data), content_type="application/json")
            else:
                response = client_method(url, data=data, format='json')
        else:
            response = client_method(url)
        assert response.status_code == status_code, f'{response.status_code} != {status_code}'
        return response
