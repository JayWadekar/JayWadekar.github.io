# images/bg/

**Optional.** Nothing in this directory is required. The site ships with a
pure-CSS background — layered gradients plus an inline SVG noise texture — and
loads no image files at all. This directory exists so a photographic
background can be dropped in later without touching any other file.

## Swapping in a photo

Redefine one custom property in `css/site.css`. Everything else (sizing,
positioning, the noise overlay) is already wired around it:

```css
:root {
    --bg-hero: url("../images/bg/whatever.jpg");
}
```

The path is relative to `css/site.css`, not to the page — hence the `../`.

To use different images for light and dark, set it a second time inside the
existing `@media (prefers-color-scheme: dark)` block.

## Expected dimensions

The layer is `background-size: cover` and `background-attachment: fixed`, so
it is scaled to fill the viewport and cropped from the centre.

| | |
|---|---|
| Recommended | **2560 × 1440** (16:9) |
| Minimum | 1920 × 1080 |
| Format | JPEG for photographs, WebP if you want it smaller |
| Target file size | **under 300 KB** — this loads on every page |

Because it is centre-cropped to the viewport, keep anything that matters away
from the edges. On a tall phone viewport roughly the middle third of the width
survives the crop.

## Raise the scrim

Gradients at 3–7% opacity cannot hurt text legibility. **A photo can.** If you
set `--bg-hero` to an image, also raise `--bg-scrim`, which sits between the
background and the text:

```css
:root {
    --bg-scrim: linear-gradient(rgba(255, 255, 255, 0.86),
                                rgba(255, 255, 255, 0.86));
}
```

and in the dark block, the same with `rgba(20, 22, 26, 0.86)`.

Then re-check contrast: body text needs **4.5:1** against the lightest point
the photo reaches behind it, and links need the same. A busy photo will need a
scrim well above 0.86, at which point very little of it is visible — which is
usually the argument for leaving the gradients alone.

## Constraints

Whatever goes here is **texture, not content**. No depicted objects, no
people, no starfields or nebulae, no simulated or AI-generated science imagery.
The background must never become something a reader could mistake for a figure.
