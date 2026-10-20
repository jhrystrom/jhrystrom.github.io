# Plan: a less narrow, more responsive site

The problem: `body { max-width: 36rem }` resolved against the 16px root, so the text column
was 536px and the font a fixed 18px at every width from tablet up. Phones were fine; laptops
and monitors got a thin strip. Fixed with CSS only. No site generator or CSS framework: either
would add more than this needed, and build.py's validation would have to be redone.

## 0. Layout tests (done)

`just test-layout` builds the site, serves it, and checks it in headless Chromium at 375 /
768 / 1280 / 1920px ([tests/test_layout.py](../tests/test_layout.py)). Failure screenshots go
to `.layout-screenshots/`; pass `--layout-screenshots` to capture every page. Checks share
one visit per page and width. Generator rules run separately with `just test`.

| Test | Pass condition | Before | After |
| --- | --- | --- | --- |
| `no_horizontal_scroll` | every page fits every viewport | fails on phones: 2 pages | passes |
| `line_length_is_readable` | 45–85 characters per line (phone: 30–85) | ~68 | 77–82 |
| `text_column_uses_wide_screens` | text column ≥ 640px at 1280px, ≥ 740px at 1920px | 536px | 689px / 767px |
| `font_size_scales` | ≥ 19px at 1280px, ≥ 21px at 1920px, ≤ 23px | 18px | 17 → 22px |
| `phone_gutters` | 16–24px each side on phones | 20px | ~21px |
| `images_break_out_on_wide_screens` | images ≥ min(natural, 1.2 × column) at 1280px+ | 536px | ~945px |
| `post_list_keeps_dates_next_to_titles` | title < 1 line below its date | 5.2 lines on phones | passes |
| `images_and_captions_are_centred_on_the_text` | image centred on text, caption below | off-centre | passes |

Runs in CI as the `layout` job, which `deploy` needs. Screenshots upload as an artifact when
it fails.

## 1. Fluid column and type (done)

- `font-size: clamp(1.0625rem, 0.95rem + 0.35vw, 1.375rem)` on `html`: ~17px on phones,
  22px on big monitors.
- Text column `--measure: 35rem`. Because the root font now scales, `rem` tracks the type
  size and line length stays 77–82 characters from tablet up. (`ch` was the earlier idea, but
  `ch` is a digit's width, much wider than an average letter, so it overshot.)
- First pass (33rem column, 20px max font) still felt narrow on wide screens; widened to
  "some of both": a bigger maximum font and a longer line.
- `overflow-wrap: anywhere` on `main`, for bare URLs like the DOI on the talk notes page.

## 2. Content fix (done)

- The surveillance capitalism post had a link spanning two list items, which Markdown can't
  render, so its raw URL showed as text. The link now sits on "two imperatives".

## 3. Wide images and code (done)

- `main` is a grid with a `content` track (`--measure`) inside a `wide` track (`--wide: 48rem`);
  articles join it via `subgrid`. Image paragraphs, `pre` and `table` use `wide`.
- Images are centred, with a muted caption below.
- The index wraps portrait and bio in `<section class="intro">`, so the float still works
  inside the grid.

## 4. Tidy-ups (done)

- One `@media (max-width: 32rem)` block. It also fixes a phone bug the old CSS had: the
  date's `flex-basis: 6.5rem` became a height when the list stacked.
- Header and footer share the text column's width.

## 5. Index two-column layout (optional, undecided)

- From ~64rem: bio and portrait left, Writing list right. Needs a test before starting.
