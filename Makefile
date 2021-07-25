test:
	pytest .

clean:
	rm -Rf dist/
	rm -Rf sparse_merkle_tree.egg-info

dev: 
	pip install --editable '.[dev]'

# PyPi package deploy
# 1. build-dist
# 2. test-pypi
# 3. update-pypi
build-dist:
	python -m build

# install twine with pipenv install -d
publish-test:
	twine upload dist/* --repository testpypi

publish:
	twine upload dist/* --repository pypi