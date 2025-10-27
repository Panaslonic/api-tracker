"""
OpenAPI Parser - парсер для OpenAPI спецификаций (JSON/YAML)
Извлекает информацию о путях, методах, параметрах
"""

import requests
import json
import yaml
from typing import Dict, Any, List


class OpenAPIParser:
    def __init__(self):
        self.session = requests.Session()

    def parse(self, url: str, method_filter: str = None) -> Dict[str, Any]:
        """Парсит OpenAPI спецификацию"""
        response = self.session.get(url, timeout=30)
        response.raise_for_status()
        
        # Определяем формат по Content-Type или расширению
        content_type = response.headers.get('content-type', '').lower()
        
        if 'yaml' in content_type or url.endswith(('.yml', '.yaml')):
            spec = yaml.safe_load(response.text)
        else:
            spec = response.json()
        
        return self._extract_api_info(spec, url, method_filter)

    def _extract_api_info(self, spec: Dict[str, Any], url: str, method_filter: str = None) -> Dict[str, Any]:
        """Извлекает ключевую информацию из OpenAPI спецификации"""
        result = {
            'url': url,
            'info': spec.get('info', {}),
            'servers': spec.get('servers', []),
            'paths': {},
            'components': {},
            'method_filter': method_filter
        }
        
        # Извлекаем информацию о путях
        paths = spec.get('paths', {})
        for path, methods in paths.items():
            # Применяем фильтр по методам, если указан
            if method_filter and method_filter not in path:
                continue
                
            result['paths'][path] = {}
            for method, details in methods.items():
                if isinstance(details, dict):
                    result['paths'][path][method] = {
                        'summary': details.get('summary', ''),
                        'description': details.get('description', ''),
                        'parameters': self._extract_parameters(details.get('parameters', [])),
                        'responses': list(details.get('responses', {}).keys()),
                        'tags': details.get('tags', []),
                        'requestBody': self._extract_request_body(details.get('requestBody', {})),
                        'operationId': details.get('operationId', '')
                    }
        
        # Извлекаем компоненты (схемы) только для отфильтрованных путей
        components = spec.get('components', {})
        if 'schemas' in components:
            if method_filter:
                # Фильтруем схемы, связанные с отфильтрованными путями
                used_schemas = self._get_used_schemas(result['paths'], components['schemas'])
                result['components']['schemas'] = used_schemas
            else:
                result['components']['schemas'] = list(components['schemas'].keys())
        
        return result

    def _extract_parameters(self, parameters: list) -> list:
        """Извлекает информацию о параметрах"""
        result = []
        for param in parameters:
            if isinstance(param, dict):
                result.append({
                    'name': param.get('name', ''),
                    'in': param.get('in', ''),
                    'required': param.get('required', False),
                    'type': param.get('schema', {}).get('type', '') if 'schema' in param else param.get('type', '')
                })
        return result

    def _extract_request_body(self, request_body: Dict[str, Any]) -> Dict[str, Any]:
        """Извлекает информацию о теле запроса"""
        if not request_body:
            return {}
        
        result = {
            'description': request_body.get('description', ''),
            'required': request_body.get('required', False),
            'content': {}
        }
        
        content = request_body.get('content', {})
        for media_type, schema_info in content.items():
            result['content'][media_type] = {
                'schema': schema_info.get('schema', {}),
                'examples': schema_info.get('examples', {})
            }
        
        return result

    def _get_used_schemas(self, paths: Dict[str, Any], all_schemas: Dict[str, Any]) -> List[str]:
        """Определяет, какие схемы используются в отфильтрованных путях"""
        used_schemas = set()
        
        def extract_schema_refs(obj):
            """Рекурсивно извлекает ссылки на схемы"""
            if isinstance(obj, dict):
                if '$ref' in obj:
                    ref = obj['$ref']
                    if ref.startswith('#/components/schemas/'):
                        schema_name = ref.split('/')[-1]
                        used_schemas.add(schema_name)
                else:
                    for value in obj.values():
                        extract_schema_refs(value)
            elif isinstance(obj, list):
                for item in obj:
                    extract_schema_refs(item)
        
        # Ищем ссылки на схемы во всех путях
        extract_schema_refs(paths)
        
        return list(used_schemas)