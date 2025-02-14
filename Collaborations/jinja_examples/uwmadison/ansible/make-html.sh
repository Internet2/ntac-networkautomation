#! /bin/bash

# Export markdown docs to HTML using `markdown` from `discount`
# package https://www.pell.portland.or.us/~orc/Code/discount/

FULLPATH=$(readlink -f "$0")
DIRNAME=$(dirname "${FULLPATH}")
DOCSDIR="${DIRNAME%%/ansible}/docs"

# Regenerate Markdown docs from Ansible playbooks
"${DIRNAME}/make-markdown.py"

# FIXME: Tried to use pydoc and sphinx but neither
#        seems to work out of the box to create either
#        a reStructuredText export or workable HTML.
#        pydoc HTML is just non-breaking spaces and line-breaks
#        with no HTML structure as defined by the RST format
#        docstrings, and Sphinx seems to require defining
#        a whole Project config and wants to build a whole
#        Read-the-Docs style templated website, not just
#        render a single file document.
#
#        I don't know if I'm the crazy one...
#
# Regenerate PyDoc HTML for scripts
# for each in ${DIRNAME}/*.py
# do
#   python3 -m pydoc "${DIRNAME}/${each}" > "${DOCSDIR}/html/${each%%.py}.html"
# done

# Regenerate HTML docs from Markdown docs
# README.md
/usr/bin/markdown -T -f autolink,definitionlist,ext,fencedcode,toc \
  -o "${DOCSDIR}/html/ns-ansible-uwmadison.html" "${DIRNAME%%/ansible}/README.md"
# use absolute paths for input filename
for each in ${DOCSDIR}/*.md
do
  # create destination filename by stripping path and extension
  FILENAME=$(basename "${each%%.md}").html
  # using `discount` Markdown processor which supports toc and fencedcode
  # along with handling multi-paragraph unordered list items consistently with Gitlab
  # over lowdown, python3-markdown or comrak each of which missed some useful property
  # `lowdown` gets special mention for having ANSI terminal and man/roff output options
  /usr/bin/markdown -T -f autolink,definitionlist,ext,fencedcode,toc \
  -o "${DOCSDIR}/html/${FILENAME}" "${each}"
  # Change internal links to point to KB URLs
  /usr/bin/sed -i -r -e 's/href=\"([a-zA-Z0-9_-]+)\.md\"/href="https:\/\/kb.wisc.edu\/ns\/internal\/\1"/g' "${DOCSDIR}/html/${FILENAME}"
done

# NB: Only import one-time MJT 20250121
# Create KB XML import format https://kb.wisc.edu/kbGuide/page.php?id=52085
# {
# echo '<?xml version="1.0"?>'
# echo '<kb_documents>'
# for each in ${DOCSDIR}/html/{netmgmt,network}*.html
# do
# FILENAME=$(basename "${each}")
# FILEBODY=$(<"${each}")
# cat - <<-EOF
#   <kb_document>
#     <kb_title>Playbook ${FILENAME%%.html}.yml</kb_title>
#     <kb_keywords>ansible playbook ${FILENAME%%.html}.yml ${FILENAME%%.html} gitlab ns-ansible-uwmadison</kb_keywords>
#     <kb_summary>Export of ns-ansible-uwmadison/docs/${FILENAME%%.html}.md</kb_summary>
#     <kb_body>${FILEBODY}</kb_body>
#     <kb_int_notes>Automated import</kb_int_notes>
#     <img_base_url> </img_base_url>
#   </kb_document>
# EOF
# done
# echo '</kb_documents>'
# } > "${DOCSDIR}/html/kb-import.xml"
