lint:
	pip install flake8
	flake8
test:
	pip install pytest pytest-cov
	pytest
