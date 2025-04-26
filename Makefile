.PHONY: clean clean-build clean-pyc clean-test lint test test-all coverage dist install dev publish help

help:
	@echo "clean - remove all build, test, coverage and Python artifacts"
	@echo "clean-build - remove build artifacts"
	@echo "clean-pyc - remove Python file artifacts"
	@echo "clean-test - remove test and coverage artifacts"
	@echo "lint - check style with flake8"
	@echo "test - run tests quickly with the default Python"
	@echo "test-all - run tests on every Python version with tox"
	@echo "coverage - check code coverage quickly with the default Python"
	@echo "dist - package"
	@echo "install - install the package to the active Python's site-packages"
	@echo "dev - install development dependencies"
	@echo "publish - publish package to PyPI"
	@echo "publish-test - publish package to TestPyPI"

clean: clean-build clean-pyc clean-test

clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr *.egg-info

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test:
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/
	rm -fr .pytest_cache

lint:
	flake8 ai_shell tests

test:
	pytest

test-all:
	tox

coverage:
	pytest --cov=ai_shell
	coverage report -m
	coverage html

dist: clean
	python setup.py sdist bdist_wheel
	ls -l dist

install: clean
	pip install .

dev:
	pip install -e ".[dev]"

publish: dist
	@echo "Publishing to PyPI..."
	@echo "Make sure you have updated the version in ai_shell/__init__.py"
	@echo "For 2FA-enabled accounts, use a PyPI API token:"
	@echo "  TWINE_USERNAME=__token__ TWINE_PASSWORD=your-token-here make publish"
	@if [ -z "$$TWINE_USERNAME" ] || [ -z "$$TWINE_PASSWORD" ]; then \
		read -p "Are you sure you want to publish to PyPI? (y/n) " answer; \
		if [ "$$answer" = "y" ]; then \
			twine upload dist/*; \
		else \
			echo "Publish canceled"; \
		fi \
	else \
		echo "Using provided credentials from environment variables"; \
		twine upload dist/*; \
	fi

publish-test: dist
	@echo "Publishing to TestPyPI..."
	@echo "For 2FA-enabled accounts, use a TestPyPI API token:"
	@echo "  TWINE_USERNAME=__token__ TWINE_PASSWORD=your-token-here make publish-test"
	@if [ -z "$$TWINE_USERNAME" ] || [ -z "$$TWINE_PASSWORD" ]; then \
		twine upload --repository-url https://test.pypi.org/legacy/ dist/*; \
	else \
		echo "Using provided credentials from environment variables"; \
		twine upload --repository-url https://test.pypi.org/legacy/ dist/* --verbose; \
	fi

# Add a version target to easily update the version
version:
	@echo "Current version: $$(grep -o '__version__ = \"[^\"]*\"' ai_shell/__init__.py | cut -d '"' -f 2)"
	@read -p "Enter new version: " new_version; \
	sed -i '' "s/__version__ = \"[^\"]*\"/__version__ = \"$$new_version\"/" ai_shell/__init__.py
	@echo "Version updated to: $$(grep -o '__version__ = \"[^\"]*\"' ai_shell/__init__.py | cut -d '\' -f 2)"
git_tag:
	# force update remote tag by local version. If remote tag exists, then delete first
	new_version=$$(grep -o '__version__ = \"[^\"]*\"' ai_shell/__init__.py | cut -d '"' -f 2) && \
	( git push origin "v$$new_version" --delete || true) && \
	( git tag -d "v$$new_version" || true) && \
	git tag -a "v$$new_version" -m "Version $$new_version" && \
	git push origin "v$$new_version" --force
