#! /usr/bin/env python3
"""Generate Markdown documentation from Ansible playbooks

Abstract
========

Create Markdown format documentation in Ansible variables at the
Play and Task level called ``__doc__`` which will be collected and
concatenated, along the Play ``name`` and Task ``name`` and a few
other attributes to create Playbook design and reference documentation.

Run ``./make-markdown.py`` in the ``ansible/`` directory which will rewrite
the ``../docs/${playbook_name}.md`` files, then check the changes into
git as normal.  Or run ``./make-html.sh`` to also generate HTML exports
for importing to the KB.

TODO
----

* TODO: Add normal CLI options so people can see what the script is for
  and enable debugging modes
* TODO: Should we use jinja2 instead of python code printing f"" strings to
  template output?  What are the pros/cons of each approach?
* TODO: use a Gitlab CI job that can push changes to run the script
  and commit the result on its own.
* TODO: research the KB API to see if we can push content changes
  from Gitlab CI jobs for publish automation. We can't push changes
  but we can make an import XML https://kb.wisc.edu/kbGuide/page.php?id=52085
  and we can try to diff active content vs checked in content,
  with a CI job that runs make-html.sh and warns if that would change
  any documents, as well as a KB API job which compares the body contents
  with the git repo HTML documents.
* TODO: add similar flow for included tasks/*.yml

Example Ansible Playbook
========================

Similar in spirit to https://github.com/andresbott/ansible-autodoc/
but with the data format being raw Markdown snippets and not using
regex parsing of specially formatted comments, but just normal YAML
data structures that can co-exist with the playbook, removing the need
to "parse" the docs at all.::
    ---
    - name: A test playbook
      hosts: all
      vars:
        __doc__: |

          A docstring paragraph

          ## Example header

          ```yaml
          ---
          foo: bar
          baz: quux
          ```
      tasks:
        - name: A task
          import_tasks: shared-tasks.yml
        - name: Another task
          vars:
            __doc__: "FIXME: should document this"
          command: "/bin/true"

    - name: An import
      vars:
        __doc__: "This playbook need to do some things after the main playbook runs"
      import_playbook: some-playbook.yml

"""

from yaml import load
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader
import os
from glob import glob
# debugging
# from pprint import pprint

kb_url = 'https://kb.wisc.edu/ns/internal'
gitlab_url = 'https://git.doit.wisc.edu/NS/ns-ansible-uwmadison/-/blob/master'
pattern_doc_url = 'https://docs.ansible.com/ansible/latest/inventory_guide/intro_patterns.html'
conditional_doc_url = 'https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_conditionals.html'

def main():
    # https://stackoverflow.com/questions/5137497/find-the-current-directory-and-files-directory
    dir_path = os.path.dirname(os.path.realpath(__file__))
    # docs_path = os.path.relpath("../docs", start=dir_path)
    docs_path = os.path.join(os.path.split(dir_path)[0], 'docs')

    for playbook_filename in glob(dir_path + "/netmgmt*.yml") + glob(dir_path + "/network*.yml"):
        # debug
        # print(f"----[ Working on {playbook_filename} ]")
        with open(playbook_filename, mode="r", encoding="utf8") as playbook_file:
            playbook_yaml = load(playbook_file, Loader=Loader)
            playbook_basename = os.path.basename(playbook_filename)
            playbook_markdown = f"""
# Playbook `{playbook_basename}`

[TOC]

- [DoIT NS Internal KB {kb_url}]({kb_url}/{os.path.splitext(playbook_basename)[0]})
- [Gitlab Documentation Source {gitlab_url}]({gitlab_url}/docs/{os.path.splitext(playbook_basename)[0]}.md)
- [Gitlab Playbook Source {gitlab_url}]({gitlab_url}/ansible/{playbook_basename})

"""
            for play in playbook_yaml:
                # debug
                # print(pprint(play))
                play_doc = ""
                play_tags = []
                play_hosts = "all"
                if "vars" in play and "__doc__" in play['vars']:
                    play_doc = play['vars']['__doc__']
                if "import_playbook" in play:
                    play_doc += f" Play imported from [{play['import_playbook']}]({play['import_playbook'].replace('.yml', '.md')})"
                if "tags" in play and play['tags'] is not None:
                    play_tags = play['tags']
                if "hosts" in play and play['hosts'] is not None:
                    play_hosts = play['hosts']

                playbook_markdown += f"\n## Play {play['name']}\n\n- [Hosts]({pattern_doc_url}): `{play_hosts}`\n- Tags: {play_tags}\n\n{play_doc}\n"

                if "tasks" in play and play['tasks'] is not None:
                    # section header
                    playbook_markdown += f"\n### Tasks {play['name']}\n\n"
                    for task in play['tasks']:
                        # debug
                        # pprint(task)
                        task_doc = ""
                        task_tags = []
                        task_when = ""
                        task_notify = ""

                        if "vars" in task and "__doc__" in task['vars']:
                            task_doc = f" {task['vars']['__doc__'].replace(chr(10), chr(10) + '  ')}"
                        if "import_tasks" in task:
                            task_doc += f"\n  Tasks imported from [{task['import_tasks']}]({task['import_tasks'].replace('.yml', '.md')})"
                        if "tags" in task and task['tags'] is not None:
                            task_tags = task['tags']
                        if "when" in task and task['when'] is not None:
                            task_when = f" ([When]({conditional_doc_url}): `{task['when']}`)"
                        if "notify" in task and task['notify'] is not None:
                            task_notify = f" (Notify: `{task['notify']}`)"

                        playbook_markdown += f"- {task['name']} (Tags: {play_tags} {task_tags}){task_when}{task_notify}{task_doc}\n"

                        if "block" in task and task['block'] is not None:
                            for block_task in task['block']:
                                block_doc = ""
                                block_tags = []
                                block_when = ""
                                block_notify = ""
                                if "vars" in block_task and "__doc__" in block_task['vars']:
                                    block_doc = f" {block_task['vars']['__doc__'].replace(chr(10), chr(10) + '  ')}"
                                if "import_tasks" in block_task:
                                    block_doc += f"\n    Block Tasks imported from [{block_task['import_tasks']}]({block_task['import_tasks'].replace('.yml', '.md')})"
                                if "tags" in block_task and block_task['tags'] is not None:
                                    block_tags = block_task['tags']
                                if "when" in block_task and block_task['when'] is not None:
                                    if task_when != "":
                                        block_when = f" ([When]({conditional_doc_url}): `{task['when']}` AND `{block_task['when']}`)"
                                    else:
                                        block_when = f" ([When]({conditional_doc_url}): `{block_when['when']}`)"
                                if "notify" in block_task and block_task['notify'] is not None:
                                    block_notify = f" (Notify: `{block_task['notify']}`)"

                                playbook_markdown += f"  - {block_task['name']} (Tags: {play_tags} {task_tags} {block_tags}){block_when}{block_notify}{block_doc}\n"
                        if "rescue" in task and task['rescue'] is not None:
                            for rescue_task in task['rescue']:
                                rescue_doc = ""
                                # Removed a lot of the cases used by `task` and `block` as I don't expect to see them in a `rescue` section
                                # but maybe I'm wrong
                                if "vars" in rescue_task and "__doc__" in rescue_task['vars']:
                                    rescue_doc = f" {rescue_task['vars']['__doc__'].replace(chr(10), chr(10) + '  ')}"
                                if "import_tasks" in rescue_task:
                                    rescue_doc += f"\n    Rescue Tasks imported from [{rescue_task['import_tasks']}]({rescue_task['import_tasks'].replace('.yml', '.md')})"

                                playbook_markdown += f"  - {rescue_task['name']}{block_doc}\n"

                if "handlers" in play and play['handlers'] is not None:
                    # section header
                    playbook_markdown += f"\n### Handlers {play['name']}\n\n"
                    for task in play['handlers']:
                        task_doc = ""
                        task_when = ""
                        task_notify = ""

                        if "vars" in task and "__doc__" in task['vars']:
                            task_doc = f" {task['vars']['__doc__'].replace(chr(10), chr(10) + '  ')}"
                        if "import_tasks" in task:
                            task_doc += f"\n  Handlers imported from [{task['import_tasks']}]({task['import_tasks'].replace('.yml', '.md')})"
                        if "when" in task and task['when'] is not None:
                            task_when = f" ([When]({conditional_doc_url}): `{task['when']}`)"
                        if "notify" in task and task['notify'] is not None:
                            task_notify = f" (Notify: `{task['notify']}`)"

                        playbook_markdown += f"- {task['name']} {task_when}{task_notify}{task_doc}\n"

        # debug
        # print(playbook_markdown)
        with open(f"{docs_path}/{os.path.splitext(os.path.basename(playbook_filename))[0]}.md", "wt", encoding="utf8") as output_markdown:
            output_markdown.write(playbook_markdown)

if __name__ == '__main__':
    main()
