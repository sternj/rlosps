# CSForAll Site Generator

This is a repository containing a static site generator, lesson plans, and documentation for
computational thinking lessons in Springfield public schools. Currently, 
only the first module of Grade 4 has been entered, but this provides
a reusable framework for entering further modules and grades.


## Outline
- `structure` contains the content and metadata for the site. 
- `render.py` takes the `.yml` files from `structure` and turns them into static html pages in `docs`. `docs` is the destination location
for compatibility with github pages. 
- `serve.sh` runs `render.py`, copies the images into the right place, then runs 
   a development server on port `5000`.
- `.github/workflows/main.yml` contains a GitHub Action that runs `render.py`, copies the images into the right place, and 
    pushes the rendered site to the `gh-pages` branch
- `docs` is the actual html of the site. Don't add it to `git`! (I haven't verified that I can force the github action to add it yet, so I haven't yet added it to `.gitignore`)
- `images` contains static images, which in both `serve.sh` and the Github action are copied into `docs`. 
- `templates` contain the `jinja2` templates that the site is built on.

Note that, as of writing, there are artifact files and folders from earlier in the prototyping process.
## Conceptual structure of site
Curriculum is organized by what `grade` it is targeted at. In each `grade`, there are one or more `module`s, each of which has one or more `lesson`s

# `yml` Specification
The structure of`structure` should look like this:

* `_index.yml`
* `grade[#].yml`
    * `_grade.yml`
    * `mod[#]`'
        * `_mod.yml`
        * `lesson[#].yml`
        
Where each `[#]` is a number or some other identifier to distinguish in the final URL path between lessons

NOTE: in `structure`, there should be **exactly one** `_index.yml`, and in each substructure, likewise in each grade and module.
**Having more than 1 `_grade.yml` per grade or more than one `_mod.yml` per module is undefined behavior**

**IMPORTANT NOTES ON FILE NAMING**: The naming of files and folders here does matter and will be reflected 
in their URLs in the final static site. For instance, module 1 of grade 4 (by the structure at the time of this writing)
will be at `/grade4/mod1/index.html`. ***Names of grade folders, module folders, and lesson files may not have any spaces or special characters in them***
## Metadata items in `yml` files
- `display_name: str` is used to show the title of that particular structure
- `ord: int` is an integer used to reflect what order to display items in lists (such as dropdowns in the navigation bar). A lower
value of `ord` corresponds to a display closer to the front in a list.

## `_index.yml`
At the moment, this only contains a placeholder key/value pair to prevent it from
being `None` when Python takes it in

## `_grade.yml`
Only contains the two top-level keys `display_name` and `ord`, as described above

## `_mod.yml`
Contains `display_name` and `ord`.

- `authors: str`: The authors of the module
- `editors: str`: the editors of a module
- `content_area: str` The discipline that this module is in
- `objectives: List[str]`: the objectives of this module
- `resource_links: List[str]`: Online resources for the module

## Lessons
Each lesson contains `display_name` and `ord`, as described above.
This `yml` specification contains a number of lists of items. These are denoted as follows:

- `key1: List`
    - `subitem1: type1`
    - `subitem2: type2`
    
This specifies that `key1` contains a list of items, each of which has 2 keys, `subitem1` and `subitem2`. This is in contrast with something marked `List[str]`, which is a list of items of a simple type (like `str`)

- `DLCS: List[str]`: DLCs for the module
- `content_standards: List`: The content standard titles and contents for the lesson
    - `name: str`: the name of the content standard
    - `text: str`: the text of the content standard
- `objectives_goals: List[str]`: the objectives and goals of the lesson
- `knowledge`
    - `label: str`: The header of the "knowledge" section
    - `items: List[str]`: The elements of the `knowledge` list
- `skills`
    - `label: str`: the header of the "skills" section
    - `items: List[str]`: the elements of the `skills` list
- `essential_questions: List[str]`: Essential questions for the lesson
- `plan_for_instruction`: A 3 column section describing what the teacher and student are doing at each section,
  as well as what the teacher should do to check whether students understand
    - `teacher_role_label, student_role_label, check_for_understanding_label: str`: The headers of the respective columns
    - `horiz_sections: List[str]`: The canonical names of the columns of the `plan_for_instruction` section. 
    - `sections: List`
        - `name: str`: The name of the section
        - `rows: List`: Each of these items represents a row in the table. Each of these fields is optional, if it isn't present then there will just be no box for that column in that row
            - `teacher_role: str`: the contents of the `teacher_role` box for that role
            - `student_role: str`: the contents of the `student_role` box for the row
            - `check_for_understanding: str`: the contents of the `check_for_understanding` box for the row
- `rlms: List`: The RLMs for that lesson
    - `[rlm-name]: List[str]`: The name of the RLM. Must be unique. Each element in the list is a component of that RLM.
         