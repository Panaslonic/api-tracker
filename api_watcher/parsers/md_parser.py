"""
Markdown Parser - парсер для Markdown документации
Извлекает заголовки второго уровня (##) и связанный контент
"""

import requests
import re
from typing import Dict, Any, List


class MarkdownParser:
    def __init__(self):
        self.session = requests.Session()

    def parse(self, url: str, **kwargs) -> Dict[str, Any]:
        """Парсит Markdown документ"""
        response = self.session.get(url, timeout=30)
        response.raise_for_status()
        
        content = response.text
        
        return {
            'url': url,
            'sections': self._extract_sections(content),
            'headers': self._extract_all_headers(content),
            'code_blocks': self._extract_code_blocks(content),
            'links': self._extract_links(content)
        }

    def _extract_sections(self, content: str) -> List[Dict[str, Any]]:
        """Извлекает секции, начинающиеся с заголовков второго уровня"""
        sections = []
        
        # Разбиваем контент на секции по заголовкам ##
        section_pattern = r'^## (.+?)$'
        matches = list(re.finditer(section_pattern, content, re.MULTILINE))
        
        for i, match in enumerate(matches):
            header = match.group(1).strip()
            start_pos = match.end()
            
            # Определяем конец секции (до следующего заголовка ## или конца документа)
            if i + 1 < len(matches):
                end_pos = matches[i + 1].start()
            else:
                end_pos = len(content)
            
            section_content = content[start_pos:end_pos].strip()
            
            sections.append({
                'header': header,
                'content': section_content,
                'subsections': self._extract_subsections(section_content),
                'code_blocks': self._extract_code_blocks(section_content),
                'links': self._extract_links(section_content)
            })
        
        return sections

    def _extract_all_headers(self, content: str) -> Dict[str, List[str]]:
        """Извлекает все заголовки по уровням"""
        headers = {
            'h1': re.findall(r'^# (.+?)$', content, re.MULTILINE),
            'h2': re.findall(r'^## (.+?)$', content, re.MULTILINE),
            'h3': re.findall(r'^### (.+?)$', content, re.MULTILINE),
            'h4': re.findall(r'^#### (.+?)$', content, re.MULTILINE)
        }
        return headers

    def _extract_subsections(self, content: str) -> List[str]:
        """Извлекает подзаголовки (### и ####) из секции"""
        subsections = []
        subsections.extend(re.findall(r'^### (.+?)$', content, re.MULTILINE))
        subsections.extend(re.findall(r'^#### (.+?)$', content, re.MULTILINE))
        return subsections

    def _extract_code_blocks(self, content: str) -> List[Dict[str, str]]:
        """Извлекает блоки кода"""
        code_blocks = []
        
        # Блоки кода с тройными обратными кавычками
        fenced_pattern = r'```(\w*)\n(.*?)\n```'
        for match in re.finditer(fenced_pattern, content, re.DOTALL):
            language = match.group(1) or 'text'
            code = match.group(2).strip()
            code_blocks.append({
                'language': language,
                'code': code
            })
        
        # Инлайн код
        inline_pattern = r'`([^`]+)`'
        inline_codes = re.findall(inline_pattern, content)
        for code in inline_codes:
            code_blocks.append({
                'language': 'inline',
                'code': code
            })
        
        return code_blocks

    def _extract_links(self, content: str) -> List[Dict[str, str]]:
        """Извлекает ссылки"""
        links = []
        
        # Markdown ссылки [text](url)
        link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        for match in re.finditer(link_pattern, content):
            text = match.group(1)
            url = match.group(2)
            links.append({
                'text': text,
                'url': url
            })
        
        return links