.PHONY: dev run test clean

# 开发模式
dev:
	uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 生产模式
run:
	uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

# 测试
test:
	uv run pytest tests/ -v

# 清理
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .ruff_cache