# How content is written

These files are copies. The originals are kept with the site's own code, where they are
tested together with what they describe. Do not edit them here: `git pull` brings the
next version.

- [AUTHORING.md](AUTHORING.md): the guide. Read it first.
- [content-types/](content-types/): one page per kind of file, and
  [fields.md](content-types/fields.md), every field of every file.
- [schemas/](schemas/): the same format as JSON Schema, for editors and tools.
- [example-course/example/](example-course/example/): a complete, valid course.

The guide was written for the site's own repository. In this kit a course is in
`courses/<course>/`, and the commands are `tools/check.py` and `tools/pack.py` (see the
README at the top). A few links in the guide lead to pages about running the site
(DEPLOYMENT.md, ARCHITECTURE.md); those are not part of the kit, and nothing in them is
needed to write content.
