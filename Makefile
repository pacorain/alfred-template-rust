WORKFLOW_FILENAME = Template

WORKFLOW_FILES = info.plist icon.png

# Running `make` with no args will clean everything up and install the 
# development version of the workflow
all: clean workflow-dev install


# The **development version** of the workflow
#
# The development version uses symbolic links to files in this folder
# so that updates get applied to your git repo.
workflow-dev:
	mkdir -p dev
	for f in ${WORKFLOW_FILES} ; do \
		ln -s "${PWD}/$$f" "dev/$$f"; \
	done;
	(cd dev && zip -ry ${WORKFLOW_FILENAME}.alfredworkflow ${WORKFLOW_FILES})
	mv -f dev/${WORKFLOW_FILENAME}.alfredworkflow .
	rm -rf dev

install-dev: workflow-dev install

workflow: ${WORKFLOW_FILENAME}.alfredworkflow

${WORKFLOW_FILENAME}.alfredworkflow:
	zip -ry ${WORKFLOW_FILENAME}.alfredworkflow ${WORKFLOW_FILES}

install: ${WORKFLOW_FILENAME}.alfredworkflow
	open ${WORKFLOW_FILENAME}.alfredworkflow

clean:
	rm -rf *.alfredworkflow dev

.PHONY: all install-dev workflow-dev workflow  install clean