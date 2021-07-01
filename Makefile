test:
	pytest .

clean:
	rm -Rf dist/
	rm -Rf smt.egg-info

# PyPi package deploy
# 1. build-dist
# 2. test-pypi
# 3. update-pypi
build-dist:
	python setup.py sdist

# install twine with pipenv install -d
test-pypi:
	twine upload dist/* --repository testpypi

update-pypi:
	twine upload dist/* --repository pypi