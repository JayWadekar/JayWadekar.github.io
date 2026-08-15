# JayWadekar.github.io

Hand-written static HTML on GitHub Pages: `index.html` (About), `research.html`,
`group.html`, `publications.html`, `videos.html`, `press.html`, one stylesheet,
`files/` for assets. **No Jekyll, no framework, no build step, no npm.** Keep it
that way. Do not replace the design with a template or theme.

## Hard constraints

These come from Jay and are not stylistic preferences:

- **No stock photography, illustrations, cartoons, icon fonts, emoji, or
  AI-generated imagery.** The only images are his headshot and real figures from
  his papers.
- **No JavaScript** unless strictly necessary. No analytics, no third-party
  embeds, no external font CDNs. (The YouTube iframes and the MathJax script on
  `research.html` predate this and are the only exceptions.)
- **Never invent** a publication, date, award, or research claim. If it cannot be
  verified, say so instead of filling the gap.
- **Never remove existing content without flagging it first.**

## Publishing

**Committing is fine. Do not push until Jay explicitly says so.** This is a
standing instruction, not a per-task one, and it holds however finished or urgent
a change looks. Commit freely at sensible boundaries, then stop; the point is
that he reviews locally, from his own folder, before anything reaches the public
site.

So keep the local preview running whenever you are editing, and give him the URL:

```bash
cd MyWebsite/JayWadekar.github.io && python3 -m http.server 8899
# http://localhost:8899/
```

It serves the working tree, so it shows the pending state whether or not it has
been committed. `git log origin/master..HEAD` is the other half of the review:
that is the list he is deciding about.

Practical consequences: unpushed commits accumulate across many turns, so
`master` sitting several commits ahead of `origin/master` is the expected state
and not something to resolve. Say how many commits are unpushed when reporting,
so nothing is lost track of.

**GitHub Pages serves `master`, the default branch.** Pushing a feature branch
publishes nothing. Merge to `master` and push that.

After a push, verify against the deployed URL, not just the push: fetch each page
and any new asset, and check that deleted files really 404. Wait on a condition
that is actually *new*, not one the old page already satisfied, or the check
passes instantly against stale content.

Git identity is set `--local` on purpose (personal gmail), so it is not attached
to UT-managed repos. Do not make it global.

## CSS

One file, `css/site.css`. Every colour is a custom property on `:root`, with a
dark palette under `prefers-color-scheme: dark`. Palette and layout patterns are
adapted from ai4astro.org (cream ground, ink text, blue accent).

**Two accent tokens, and collapsing them into one reintroduces a real bug:**

- `--accent`: section rules, borders, focus rings. Shapes, not letterforms.
- `--accent-ink`: accent-coloured *text* (links, active nav). Darker.

The page carries a faint background tint, and the brand blue as body-size text
sits too close to the WCAG AA line to survive it. The previous UT burnt orange
was worse: `#BF5700` measures 4.59:1 on pure white, clearing AA by 0.09, so a
background even 1% off white failed.

## Verify by measuring, not by looking

Two mistakes this codebase has already produced, both caught only by measurement:

1. **Headless Chrome clamps windows to a 500px minimum.** A "375px" screenshot
   silently renders at 500px and shows clipping that does not exist. Drive Chrome
   over CDP with `Emulation.setDeviceMetricsOverride` instead.
2. **Sampling a rendered page for background contrast picks up link glyphs and
   the headshot**, and reports nonsense. Hide the content first
   (`document.querySelectorAll('body > *').forEach(e => e.style.visibility = 'hidden')`),
   screenshot, then sample.

Check `document.documentElement.scrollWidth - clientWidth === 0` on every page at
375, 768 and 1440px in both colour schemes. And when a colour looks wrong, sample
the pixel before changing anything. Twice now a rule that looked grey measured
as exactly the accent.

## Generated content

`scripts/build_snippets.py` queries ADS and writes two fragments to
`scripts/out/`, for pasting between the `BEGIN/END generated` markers:

- `collaborators.html` → **`group.html`**
- `topics.html` → **`index.html`**

```bash
ADS_DEV_KEY=$(cat ~/.ads/dev_key) python3 scripts/build_snippets.py
```

Nothing runs in the browser; re-running the script is the only way these change.
Two things in it are deliberate: `GROUP` excludes people listed by hand elsewhere
so nobody appears twice, and `OVERRIDE_AFF` exists because ADS reports the
affiliation a co-author had *when the paper was published*, which goes stale.

## Citing papers

**`../../References/papers.md`** is a local ADS-derived cache of every paper's
title, abstract and arXiv id, refreshed by `update_papers.py` beside it. It is
outside this repo and untracked. Take arXiv ids from it, never from memory, and
check the id back against the title before attaching it to a claim.

## Figures from papers

Source PDFs live in `../../References/Figures/`. Ghostscript renders them onto
its own default page, so **autocrop to the ink** or you get a postage stamp in a
sea of white. Render at 300dpi, crop, scale to 1600px wide, save optimized PNG.

Captions: ask Jay what a figure shows rather than inferring it. Details like
"eccentric" or "resummed" are not recoverable from the plot, and a confident
wrong caption is worse than a thin one.

Use `<figure class="wide">` for data-heavy plots: it bleeds symmetrically past
the text column and stays inside the viewport.

## The CV PDF

`files/CV_JayWadekar.pdf` is tracked here, and has to be: Pages has no build
step, so the file the nav links to must exist in the repo. Its diffs are
therefore unreadable, which is expected, not a problem to solve here.

**The `.tex` in `../../CV_Academic` is deliberately not version controlled.**
Jay's decision: the PDF committed here is the record, and he does not want the
source tracked. Do not offer to change that. It also must not go into a public
repo regardless: line 58 is a commented-out personal mobile number that is
absent from the compiled PDF, and Pages serves every file verbatim.

Committing the PDF is the right call here, not a compromise. The alternatives
are worse: a CI job to build LaTeX on push adds the build step this site exists
without, an external host adds link rot to a nav link, and **Git LFS would break
the site outright, because Pages does not resolve LFS pointers and would serve
the pointer file instead of the PDF.** The cost is small and measured: 19
revisions of the PDF come to 2.6 MB uncompressed in a 12 MB repo, where single
figures like `files/Jan2019.pdf` are larger than the CV's entire history.

`.gitattributes` sets a `diff=pdf` driver so `git diff` can show what changed in
the PDF text. It needs one local config line, documented in that file.

Updating the CV means: edit the `.tex`, rebuild and measure the margins per
`CV_Academic/CLAUDE.md`, then copy the result here and commit. Both halves, one
task.

## Still open

- `index.html` has an HTML-comment TODO in the gravitational-wave research
  direction, about naming his most striking individual detection.
- Footer wants an arXiv author link and an ORCID iD; neither has been supplied.
- `group.html` entries have no photos. Jay is asking his group for them. Do not
  source someone's photo from a search result. `ul.people` rows collapse
  cleanly to text without an `<img>`, so photos drop in later with no restyling.
