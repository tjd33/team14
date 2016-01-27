all: ./docs/design_documents/*
	f="$(shell ls ./docs/design_documents | grep .tex)"

	pdflatex ./docs/design_documents/$(shell ls ./docs/design_documents | grep .tex) -output-directory="./docs/design_documents"
other:
	pdflatex files

test:
	python3 -m unittest discover -v
