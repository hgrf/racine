test:
	python -m pip install --upgrade pip
	pip install -r requirements.txt
	pip install coverage pytest
	coverage run -m pytest