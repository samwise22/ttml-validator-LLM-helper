# BBC Subtitle Guidance Knowledge Base

Source: `BBC-SUBTITLES-V1.2.5` in `SOURCES.md`.

This is a selective routing layer, not a copy of the BBC guide. A report generator shall insert only entries that materially relate to a validator finding or a separately labelled editorial observation. The `Guidance` text below is a repository-authored paraphrase; it shall not be presented as a BBC quotation.

Where an entry contains `Verified excerpt`, the report may reproduce that exact short extract in quotation marks and shall attribute it to the BBC Subtitle Guidelines. The wording shall not be changed inside the quotation. Entries without that field shall use paraphrase and link only.

## Dynamic inclusion rules

1. Match a finding to one or more `Signals`. Signals are concepts, not validator codes.
2. Confirm the supplied TTML or validator evidence supports the match.
3. Insert the entry's title, guidance paraphrase, and exact deep link inside that finding.
4. Do not insert unrelated entries merely to make a report appear comprehensive.
5. Do not recast presentation advice as a validator error.
6. If a finding concerns an exact TTML construct, prefer the relevant file-format entry over a broader presentation entry.

## Curated entries

### BBC-LINE-LENGTH

- Signals: line length, characters per line, wrapping, long subtitle
- Guidance: Keep subtitle lines within appropriate readable lengths and resolve excessive length through considered editing or line division.
- Verified excerpt: “the number of characters within a region does not exceed 37”
- Link: https://www.bbc.co.uk/accessibility/forproducts/guides/subtitles/#Line-length

### BBC-NUMBER-OF-LINES

- Signals: number of lines, excessive lines, three-line subtitle
- Guidance: Choose the number of displayed lines with readability and the visible image in mind.
- Link: https://www.bbc.co.uk/accessibility/forproducts/guides/subtitles/#Number-of-lines

### BBC-NATURAL-LINE-BREAKS

- Signals: line break, `tt:br`, awkward wrapping, phrase split
- Guidance: Place breaks at natural linguistic boundaries so the subtitle remains easy to parse.
- Link: https://www.bbc.co.uk/accessibility/forproducts/guides/subtitles/#Break-at-natural-points

### BBC-MINIMUM-TIMING

- Signals: duration, display time, reading speed, short subtitle
- Guidance: Allocate sufficient display time for the subtitle to be read, while balancing speech, pictures, and editing.
- Verified excerpt: “recommended rate of 160-180 words per minute”
- Link: https://www.bbc.co.uk/accessibility/forproducts/guides/subtitles/#Target-minimum-timing

### BBC-CONSISTENT-TIMING

- Signals: inconsistent duration, variable reading rate, timing pattern
- Guidance: Apply timing decisions consistently across comparable subtitles.
- Link: https://www.bbc.co.uk/accessibility/forproducts/guides/subtitles/#Use-consistent-timing

### BBC-GAPS

- Signals: gap, adjacent subtitle, subtitle interval, timing collision
- Guidance: Manage gaps between consecutive subtitles deliberately to support readable transitions.
- Link: https://www.bbc.co.uk/accessibility/forproducts/guides/subtitles/#Gaps

### BBC-SYNCHRONISATION

- Signals: synchronisation, speech onset, timing offset, lag
- Guidance: Synchronise subtitle appearance with speech and minimise avoidable lag.
- Link: https://www.bbc.co.uk/accessibility/forproducts/guides/subtitles/#Synchronisation

### BBC-SPEAKER-IDENTIFICATION

- Signals: speaker, colour, horizontal position, dash, label, voice-over
- Guidance: Use an appropriate and consistent method to make speaker changes clear.
- Link: https://www.bbc.co.uk/accessibility/forproducts/guides/subtitles/#Identifying-speakers

### BBC-COLOURS

- Signals: `tts:color`, `tts:backgroundColor`, contrast, speaker colour
- Guidance: Apply foreground and background colours in ways that preserve readability and consistent speaker identification.
- Link: https://www.bbc.co.uk/accessibility/forproducts/guides/subtitles/#Colours

### BBC-TYPOGRAPHY

- Signals: `tts:fontFamily`, `tts:fontSize`, font, text size, character support
- Guidance: Use supported, readable typography and appropriate presentation sizing.
- Link: https://www.bbc.co.uk/accessibility/forproducts/guides/subtitles/#Typography

### BBC-POSITIONING

- Signals: `tts:origin`, region position, horizontal position, vertical position
- Guidance: Position subtitles to remain readable without unnecessarily obscuring important visual information.
- Link: https://www.bbc.co.uk/accessibility/forproducts/guides/subtitles/#Positioning

### BBC-EBU-TT-D-CONFORMANCE

- Signals: EBU-TT-D, IMSC profile, conformance, profile
- Guidance: BBC EBU-TT-D documents are governed by the stated IMSC text-profile conformance requirements.
- Link: https://www.bbc.co.uk/accessibility/forproducts/guides/subtitles/#Conformance-with-IMSC-1-0-1-Text-Profile

### BBC-TT-ATTRIBUTES

- Signals: root `tt:tt`, missing root attribute, language, namespace
- Guidance: Apply the required document-level attributes and namespace declarations to the TTML root element.
- Link: https://www.bbc.co.uk/accessibility/forproducts/guides/subtitles/#tt-tt-attributes

### BBC-TIMEBASE

- Signals: `ttp:timeBase`, time base, frame timing, clock timing
- Guidance: Declare and use the TTML time base consistently with the document's timing expressions.
- Link: https://www.bbc.co.uk/accessibility/forproducts/guides/subtitles/#ttp-timeBase

### BBC-CELL-RESOLUTION

- Signals: `ttp:cellResolution`, cell resolution
- Guidance: Use the required cell-resolution declaration and values for the target document profile.
- Link: https://www.bbc.co.uk/accessibility/forproducts/guides/subtitles/#ttp-cellResolution

### BBC-ACTIVE-AREA

- Signals: `ittp:activeArea`, active area
- Guidance: Declare the active image area in accordance with the target presentation profile.
- Link: https://www.bbc.co.uk/accessibility/forproducts/guides/subtitles/#ittp-activeArea

### BBC-STYLE-APPLICATION

- Signals: style reference, styling attribute, `xml:id`, inherited style
- Guidance: Apply style attributes and references through the TTML structures permitted by the target profile.
- Verified excerpt: “must be applied to content elements”
- Link: https://www.bbc.co.uk/accessibility/forproducts/guides/subtitles/#Applying-style-attributes-to-content-elements

### BBC-REGIONS

- Signals: `tt:region`, region reference, `tts:extent`, `tts:displayAlign`, `tts:writingMode`, `tts:overflow`
- Guidance: Define and reference regions using the permitted geometry, alignment, writing-mode, and overflow properties.
- Link: https://www.bbc.co.uk/accessibility/forproducts/guides/subtitles/#Regions

### BBC-CONTENT-ELEMENTS

- Signals: `tt:div`, `tt:p`, `tt:span`, `tt:br`, content model
- Guidance: Structure subtitle content with the TTML content elements and nesting permitted by the target profile.
- Link: https://www.bbc.co.uk/accessibility/forproducts/guides/subtitles/#Content-Elements

### BBC-VALIDATION

- Signals: validation workflow, validator, online distribution
- Guidance: Use the documented validation workflow for an EBU-TT-D document intended for online distribution.
- Link: https://www.bbc.co.uk/accessibility/forproducts/guides/subtitles/#Appendix-Validating-an-EBU-TT-D-file
