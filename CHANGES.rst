Changelog
=========


0.2.1 (2016-12-21)
------------------

- Handle problems with malformed html that etree are unable to parse.
  Transformation is skipped and a warning log message is send.
  [cekk]


0.2.0 (2016-12-14)
------------------

- Avoid etree.tostring to auto close empty divs with `method="html"` parameter.
  This prevents some problems with browsers that don't like self-closed div
  and renders a wrong html.
  [cekk]


0.1.2 (2015-12-09)
------------------

- Fix additional infos position when a link has some children (for example a span)
  [cekk]


0.1.1 (2015-12-03)
------------------

- Handled UnicodeDecodeError in Transform
  [cekk]


0.1.0 (2015-12-02)
------------------

- Initial release.
  [cekk]
