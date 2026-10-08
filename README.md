# CMRDF project website

Static English project page for **CMRDF: Morphology-Conditioned Reachability Fields for Task-Space Robot Policy Transfer**, accepted at CoRL 2026.

## Stable publication targets

- Home: https://cmrdf-project.github.io/
- Interactive view: https://cmrdf-project.github.io/interactive/
- Paper: https://cmrdf-project.github.io/static/pdfs/cmrdf.pdf
- Website repository: https://github.com/cmrdf-project/cmrdf-project.github.io

These are the intended permanent addresses; see the deployment status delivered with the project for verification. The research code is currently **Code release in preparation**.

## Preview locally

Run from this directory:

```bash
python3 -m http.server 8765 --bind 127.0.0.1
```

Open http://127.0.0.1:8765/. Use HTTP rather than double-clicking `index.html`, because the iframe's loading and error messages use same-origin messaging. No build step, Node, database, or model server is required.

## Editing

| Change | Location |
| --- | --- |
| Title, authors, affiliations, abstract, method text | `index.html` |
| Colors, typography, mobile layout | `static/css/site.css` |
| Figure 1 / Figure 2 | `static/images/overview.png`, `static/images/method.png` |
| Published paper | `static/pdfs/cmrdf.pdf` |
| Interactive landing page and instructions | `interactive/index.html` |
| Full visualization data and inline Plotly | `interactive/orientation_anchor_visualization.html` |
| Anchor control and rendering behavior | `static/js/visualization.js` |
| Click-to-load, error/retry UI, BibTeX copy | `static/js/site.js` |
| Real visualization screenshot / social image | `static/images/interactive-preview.png`, `static/images/social-preview.png` |
| Code release status and future repository link | `#code` and the Code button in `index.html` |
| Citation and scholarly metadata | `#citation` and `<head>` in `index.html`; shared metadata also in `interactive/index.html` |

The current PDF, abstract, authors and figures come from the approved camera-ready version. Paper and figure assets are byte-for-byte copies. Do not overwrite original research files when updating the website. Do not add unconfirmed author links, arXiv/DOI/proceedings identifiers, or release dates.

When a video is available, place an appropriately sized MP4 under `static/videos/`, and add a `<video controls playsinline preload="metadata" poster="…">` block. No empty video placeholders are included in this version.

## Updating the original interactive export

```bash
python3 scripts/update_interactive.py /path/to/original/orientation_anchor_visualization.html
```

The script reads the original without modifying it. It preserves all coordinates and orientation-support values, uses the original cumulative visibility masks, and retains the inline Plotly library. It adds the publication viewer's initial visibility and presentation settings. The page's HTML range control replaces the small Plotly slider visually and supports keyboard operation. At N=0 there is only the position cloud; at N=100 all 100 anchor/projection pairs are visible. Default: N=1. The background cloud is restyled with low-opacity gray points for readability. Run browser verification and recapture the screenshot after updating data.

The homepage creates no visualization iframe or Plotly request until **Explore in 3D** is clicked. The dedicated view loads it automatically. Local-only assets keep this independent of external CDNs. The viewer reports ready/error states to its same-origin parent; failures have a retry button and standalone link.

## GitHub Pages deployment

1. Use the public repository `cmrdf-project/cmrdf-project.github.io` under the organization.
2. Push the website files to `main` (or preserve an existing publishing branch when adopting an existing repository).
3. In **Settings → Pages**, select **Deploy from a branch**, branch **main**, folder **/ (root)**.
4. Keep `.nojekyll` at the root. No custom Actions workflow is needed.
5. Wait for Pages deployment to finish, then verify the home page, `/interactive/`, and the PDF from a signed-out session.

Keep the organization, repository name, and published paper path stable. Later updates can use ordinary commits to the same publishing branch.

## Browser verification

Install Playwright in a development-only virtual environment, install its Chromium browser, start the local preview above, then run:

```bash
python scripts/verify_site.py --base-url http://127.0.0.1:8765 --output-dir /tmp/cmrdf-site-check
```

Checks cover initial loading, all key anchor counts, drag/zoom/reset, clipboard, desktop and mobile layout, 404/error recovery, and WebGL failure. The script writes screenshots and a JSON report outside the site. The original-data and paper comparisons were additionally checked in the local source workspace.

## Attribution

Adapted from [Academic Project Page Template](https://github.com/eliahuhorwitz/Academic-project-page-template), based in part on [Nerfies](https://nerfies.github.io/). See [LICENSE.md](LICENSE.md) for the website's CC BY-SA 4.0 terms and bundled library notices. This does not choose a license for the unreleased research code.
