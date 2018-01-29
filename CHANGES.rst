Changelog
=========


0.4.3 (2018-01-29)
------------------

- Use set() to remove duplicated entries in link detection
  [cekk]


0.4.2 (2018-01-29)
------------------

- Fix xpath filter to get all old-style internal-links
  [cekk]


0.4.1 (2017-12-18)
------------------

- Fixed unicode.
  [daniele]


0.4.0 (2017-12-11)
------------------

- Add support for Plone5
  [cekk]


0.3.0 (2017-01-26)
------------------

- Parse only links with `internal-link` class
  [cekk]

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
