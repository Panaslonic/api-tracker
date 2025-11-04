# Makefile для API Watcher

.PHONY: help install test test-unit test-integration test-coverage test-quick clean lint format

# Цвета для вывода
GREEN = \033[0;32m
YELLOW = \033[1;33m
RED = \033[0;31m
NC = \033[0m # No Color

help: ## Показать справку
	@echo "$(GREEN)API Watcher - Доступные команды:$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}'

install: ## Установить зависимости
	@echo "$(GREEN)Установка зависимостей...$(NC)"
	pip install -r requirements.txt

test: ## Запустить все тесты
	@echo "$(GREEN)Запуск всех тестов...$(NC)"
	python run_tests.py all

test-unit: ## Запустить только юнит тесты
	@echo "$(GREEN)Запуск юнит тестов...$(NC)"
	python run_tests.py unit

test-main: ## Запустить тесты основного модуля
	@echo "$(GREEN)Запуск тестов основного модуля...$(NC)"
	python run_tests.py main

test-integration: ## Запустить интеграционные тесты
	@echo "$(GREEN)Запуск интеграционных тестов...$(NC)"
	python run_tests.py integration

test-coverage: ## Запустить тесты с отчетом о покрытии
	@echo "$(GREEN)Запуск тестов с покрытием кода...$(NC)"
	python run_tests.py coverage

test-quick: ## Быстрые тесты (остановка на первой ошибке)
	@echo "$(GREEN)Запуск быстрых тестов...$(NC)"
	python run_tests.py quick

lint: ## Проверить код линтером
	@echo "$(GREEN)Проверка кода линтером...$(NC)"
	@if command -v flake8 >/dev/null 2>&1; then \
		flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics; \
		flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics; \
	else \
		echo "$(YELLOW)flake8 не установлен. Установите: pip install flake8$(NC)"; \
	fi

format: ## Форматировать код
	@echo "$(GREEN)Форматирование кода...$(NC)"
	@if command -v black >/dev/null 2>&1; then \
		black . --line-length 127; \
	else \
		echo "$(YELLOW)black не установлен. Установите: pip install black$(NC)"; \
	fi

clean: ## Очистить временные файлы
	@echo "$(GREEN)Очистка временных файлов...$(NC)"
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage
	rm -rf dist
	rm -rf build

run: ## Запустить API Watcher
	@echo "$(GREEN)Запуск API Watcher...$(NC)"
	python main.py

run-health: ## Проверить состояние здоровья
	@echo "$(GREEN)Проверка состояния здоровья...$(NC)"
	python main.py --health-check

setup-dev: install ## Настроить среду разработки
	@echo "$(GREEN)Настройка среды разработки...$(NC)"
	@if ! command -v pytest >/dev/null 2>&1; then \
		pip install pytest pytest-asyncio pytest-mock pytest-cov; \
	fi
	@if ! command -v flake8 >/dev/null 2>&1; then \
		pip install flake8; \
	fi
	@if ! command -v black >/dev/null 2>&1; then \
		pip install black; \
	fi
	@echo "$(GREEN)Среда разработки настроена!$(NC)"

ci: clean lint test-coverage ## Запустить CI pipeline
	@echo "$(GREEN)CI pipeline завершен$(NC)"

# Алиасы для удобства
t: test
tu: test-unit
ti: test-integration
tc: test-coverage
tq: test-quick