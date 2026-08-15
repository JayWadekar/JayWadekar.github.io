# jaywadekar.github.io

Source for [jaywadekar.github.io](https://jaywadekar.github.io), the personal
academic site of Jay Wadekar, assistant professor of physics at UT Austin.

Hand-written static HTML, served by GitHub Pages from `master`. No framework, no
build step, no dependencies: editing a file and pushing is the whole deployment.

```
index.html         about, research directions, software, news
research.html      selected research projects
group.html         group members, past students, frequent collaborators
publications.html  links to ADS and Google Scholar
videos.html        recorded talks
press.html         press coverage

css/site.css       the entire stylesheet
files/             CV, figures, headshot
scripts/           regenerates the collaborator and topic lists from NASA ADS
```

Preview locally with:

```bash
python3 -m http.server 8899
```

Originally built from a website template shared by Chang Hahn, with thanks; the
markup and stylesheet have since been rewritten.
