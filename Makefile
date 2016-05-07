all: ./docs/design_documents/*
	f="$(shell ls ./docs/design_documents | grep .tex)"

	pdflatex ./docs/design_documents/$(shell ls ./docs/design_documents | grep .tex) -output-directory="./docs/design_documents"
other:
	pdflatex files

test:
	python3 -m unittest discover -v

python:
	sudo pip3 install -r requirements.txt --upgrade

website:
	python3 -m senseable_gym.sg_view.run

demo:
	python3 -m senseable_gym.sg_run.html_tester

design:
	python3 -m senseable_gym.sg_run.design_night_tester

clean:
	find . | grep -E "(__pycache__|\.pyc|\.pyo$\)" | xargs rm -rf
