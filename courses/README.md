# Your course goes here

Download your course's files on the site (Educators, **Download the course files**) and
unpack the zip with the kit's tool:

```
uv run tools/unpack.py ~/Downloads/rl.zip
```

```
courses/
  rl/
    course.yaml
    content/        what the site shows: your assistant writes here
    source/         you add this: slides, labs, homework, past papers. Ignored by git.
```

Git keeps track of your course in your copy of the kit, on your computer only. The
repository you cloned never has a course in it, and nothing here is ever pushed.
