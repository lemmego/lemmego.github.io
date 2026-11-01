# Gophers

Vendored from [egonelbre/gophers](https://github.com/egonelbre/gophers),
which is **CC0 1.0** — public domain, no attribution required. The gopher
itself was designed by Renée French.

They arrive as Inkscape files carrying RDF metadata and editor state, which
is most of their weight and none of their picture. `scripts/gophers.py` runs
svgo over them and writes `data/gophers.yaml` with each one's intrinsic size,
so the `<img>` can reserve its space before it loads. 2.8MB in, 1.6MB out.

Filenames are flattened and renamed for what they are used for here rather
than where they sat upstream — `music-broadcast` is `computer/music.svg`,
`music-party` is `party/music.svg`. The mapping from documentation section
to gopher lives in `layouts/partials/custom/page-begin.html`.

To add one: put the upstream path in `scripts/gopher-list.txt`, run
`python3 scripts/gophers.py`, and add the section to that partial's map.
