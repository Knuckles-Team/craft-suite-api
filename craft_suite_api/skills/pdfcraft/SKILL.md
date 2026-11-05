---
name: pdfcraft
description: PdfCraft PDF processing — documents, forms, text, bookmarks, OCR, redactions and signatures.
---

# Pdfcraft

## When to use

PdfCraft PDF processing — documents, forms, text, bookmarks, OCR, redactions and signatures.

## Activation

Call `registry_activate` with the namespace `pdfcraft` before using any `pdfcraft_*` tool.

## Files in and out

Pass an input file as `exchange://<sink>/<key>` (for example `exchange://files/in/photo.png`) or as an `https` URL; the server stages it and hands the app a local path. Give an output path as a relative path such as `out.png`: it lands in this run's folder, and after the call the result links each output in every configured sink.

## Tools

| Tool | What it does |
|---|---|
| `pdfcraft_accessibility_autotag_apply` | Write marked content, a Document structure element, paragraph tags and a parent tree for every text object in an untagged, text-only PDF. |
| `pdfcraft_accessibility_autotag_form_fields` | Write `/Form` tags, widget structure-parent keys, and a parent tree for all page widgets in an untagged AcroForm. |
| `pdfcraft_accessibility_autotag_preview` | Propose paragraph and heading tags for visible text blocks on one page. |
| `pdfcraft_accessibility_check` | Run the Accessibility Checker's full check (32 rules in 7 categories: document, page_content, forms, alternate_text, tables, lists, headings). |
| `pdfcraft_accessibility_figures` | The tagged figures (Figure elements, through the role map) in document order: figure number, page, alternate text and where the figure is drawn (top-left-origin points). |
| `pdfcraft_accessibility_find_untagged` | Find untagged painted page content, annotations, and form widgets. |
| `pdfcraft_accessibility_fix` | Apply the checker's automatic fix for a rule: primary-language (value: the language, e. |
| `pdfcraft_accessibility_mark_tag_artifact` | Mark a reachable leaf structure tag's direct marked content as an artifact and remove the tag from the reading structure. |
| `pdfcraft_accessibility_move_tag` | Move a reachable indirect structure tag before or after a direct sibling in their parent's /K array, changing tagged reading order without changing page appearance. |
| `pdfcraft_accessibility_report` | Run the full check and write the accessibility report (HTML) to path; returns the results too. |
| `pdfcraft_accessibility_review_html` | Compare two open versions of a PDF and write a self-contained HTML summary of the same evidence as accessibility_review_record: document hashes, outcome counts, rule changes, and rules still requiring review. |
| `pdfcraft_accessibility_review_load` | Read a local review sidecar only when its recorded SHA-256 matches the open PDF. |
| `pdfcraft_accessibility_review_record` | Compare the same accessibility rules on two open versions of a PDF and write a JSON record to path. |
| `pdfcraft_accessibility_review_save` | Write a local JSON sidecar for an open PDF with rule-level human review decisions. |
| `pdfcraft_accessibility_set_alt` | Set a figure's alternate text (alt; empty or omitted clears it), or mark it decorative (decorative: true: its content becomes an artifact and the figure leaves the tags). |
| `pdfcraft_accessibility_set_tag_property` | Set or clear one property of a reachable indirect structure tag. |
| `pdfcraft_accessibility_tag_content` | List the marked-content references directly owned by one reachable indirect structure tag, including page, MCID and extracted text. |
| `pdfcraft_accessibility_tags` | List reachable indirect structure tags in document order with PDF object number, generation, nearest indirect parent, depth, page, type, title, actual text, alternate text, language, a table's summary and a header cell's scope, one page at a time: count is how many tags match, next the offset of the following page (null at the end). |
| `pdfcraft_action_list` | Action Wizard: the built-in actions (name, description, steps) and every step an action can use (id, label, whether it takes a text argument). |
| `pdfcraft_action_run` | Action Wizard: run a built-in action (action: its name) or a list of steps ([{step, arg}], ids from action_list) on each PDF in paths, writing the results into folder under the same names. |
| `pdfcraft_attachment_add` | Attach the file at path to the document (document level, the Attachments panel; not a paper-clip comment on a page). |
| `pdfcraft_attachment_delete` | Remove the document-level attachment with this name (as doc_info lists it). |
| `pdfcraft_bookmark_add` | Add a bookmark that goes to a page, under a parent bookmark (or at the top level), at a position. |
| `pdfcraft_bookmark_delete` | Delete a bookmark and the bookmarks under it. |
| `pdfcraft_bookmark_from_structure` | Make bookmarks from the document's tagged headings (H, H1-H6), nested by level under a new first bookmark titled "Untitled". |
| `pdfcraft_bookmark_from_text_styles` | Make bookmarks from the lines set in chosen text styles, for documents whose headings are not tagged: levels lists one style per bookmark level ({font, size, bold, italic} as text_styles gives them; sizes within a quarter point match), the first level 1, the next nested under the bookmark before it, and so on. |
| `pdfcraft_bookmark_list` | The bookmarks in outline order, one page at a time: each with its path (1-based, as the other bookmark tools take it), title, target page and open state, its colour ([r, g, b], 0-1) and bold or italic style when it has them, and its children on the same page. |
| `pdfcraft_bookmark_move` | Move a bookmark (with its children) under another parent, or within its level. |
| `pdfcraft_bookmark_rename` | Change a bookmark's title. |
| `pdfcraft_bookmark_set_page` | Point a bookmark at another page. |
| `pdfcraft_bookmark_set_style` | Colour a bookmark's title and make it bold or italic (ISO 32000-2 §12. |
| `pdfcraft_command_batch` | Run steps in order (at most 1000). |
| `pdfcraft_command_list` | Every registered PdfCraft command with its menu, shortcut, whether it is enabled now, and the tool that automates it. |
| `pdfcraft_command_run` | Run a registry command through its headless tool. |
| `pdfcraft_comment_add` | Add a comment as Acrobat's commenting tools do. |
| `pdfcraft_comment_delete` | Delete a comment with its pop-up and replies, or one reply (its id, or page and index, from comment_list) with its pop-up and the replies to it; the comment and its other replies stay. |
| `pdfcraft_comment_edit` | Change a comment's text, colour, opacity, line width, font size (text box/typewriter/callout), fill (rectangle/oval/polygon/text box/callout; "none" removes it), rectangle (rectangle/oval/text box/stamp), position (`move` [dx, dy] in points) or shape (`points`: a line's two ends, or the corners of connected lines, a polygon or a cloud). |
| `pdfcraft_comment_image_preview` | Return a PNG of the page without the selected image signature/initials (layer=background, default), or its embedded image with alpha (layer=image). |
| `pdfcraft_comment_list` | Every comment (annotation other than links, form widgets and pop-ups) with its page, index, id, type, author, text, date, rectangle, colour, review status, checkmark and replies (each with its own status and checkmark). |
| `pdfcraft_comment_lock` | Lock or unlock a comment (Properties ▸ Locked). |
| `pdfcraft_comment_mark` | Mark or unmark a comment with a checkmark (Acrobat: Mark with checkmark), recorded as a private reply. |
| `pdfcraft_comment_reply` | Add a reply to a comment's thread. |
| `pdfcraft_comment_set_status` | Set a comment's review status (Acrobat: Set status), recorded as a status reply. |
| `pdfcraft_comments_hide` | Hide or show every comment on the page (fields and links still draw). |
| `pdfcraft_comments_summarize` | Make a PDF summarising every comment (number, author, type, date, text, replies), sorted by page, author, date or type. |
| `pdfcraft_content_copy` | Copy an added item (page, index from content_list) and paste it, as Edit ▸ Copy and Paste do: onto to_page of to_doc (by default its own page and document) as it is: a text box's text, font, size, colour, alignment and box; an image's picture, box, turns, flips and crop (within its document the same image object is drawn again; into another one the picture goes as its JPEG or JPEG 2000 file, or else a PNG, without a colour profile and with CMYK colours turned to RGB). |
| `pdfcraft_content_delete` | Delete an added item (page, index from content_list). |
| `pdfcraft_content_list` | Text and images added with page_add_text/page_add_image (or Edit a PDF ▸ Add content), per page with a 1-based index, rect (points from the top-left of the page), and text style. |
| `pdfcraft_content_update` | Move/resize (rect), retype (text) or restyle (font, size, bold, italic, color, align, char_spacing in points) an added item (page, index from content_list). |
| `pdfcraft_doc_audit_redactions` | Find faux redactions: opaque filled rectangles painted over text that is still extractable, and /Redact annotations that were marked but never applied. |
| `pdfcraft_doc_audit_space` | How many bytes each kind of content takes and its share of the file (PDF Optimizer ▸ Audit space usage): images, content streams, fonts, forms, comments, structure, bookmarks, … and document overhead. |
| `pdfcraft_doc_backdrops` | Pages that paint their own backdrop, which hides a background added behind the content: `fill` (an opaque white fill doc_background can replace) or `image` (a page-sized picture, e. |
| `pdfcraft_doc_background` | Fill page backgrounds with a colour, or a picture from `file` (an image, or page `file_page` of a PDF) fitted at `scale` (default 1), behind the content. |
| `pdfcraft_doc_batch` | Run convert, ocr and/or optimize over files and folders, one file at a time. |
| `pdfcraft_doc_bates_multi` | Apply one consecutive Bates sequence to an ordered list of PDFs. |
| `pdfcraft_doc_close` | Close a document. |
| `pdfcraft_doc_combine` | Combine files, in order, into one PDF (bookmarks are kept under one entry per file). |
| `pdfcraft_doc_compare` | Compare the text of two open documents: other is the older version, doc the newer. |
| `pdfcraft_doc_compare_mark` | Add the differences from other (older) to doc (newer) as comments in doc: highlights over replaced (blue) and inserted (green) text, notes where text was deleted (red), authored Compare. |
| `pdfcraft_doc_compare_report` | Write the compare summary report (a PDF listing every change) to path. |
| `pdfcraft_doc_create` | Create a new, unsaved document and return it like doc_open: `blank` (pages, width, height in points; default 1 US Letter page), `images` (paths of PNG, JPEG, TIFF (every page), GIF or BMP files, one page each at the image's resolution) or `text` (a . |
| `pdfcraft_doc_create_multiple` | Convert several files (PDFs, PNG/JPEG/JPEG 2000/TIFF/GIF/BMP images, . |
| `pdfcraft_doc_export_all_images` | Write the images that pages use into a folder (`<name>_Page_<n>_Image_<k>. |
| `pdfcraft_doc_export_data` | Write comments and/or form data to path; the extension picks the format: . |
| `pdfcraft_doc_export_images` | Write pages as PNG, JPEG or TIFF files (`<name>_page_<n>. |
| `pdfcraft_doc_export_office` | Export a PDF ▸ Word (. |
| `pdfcraft_doc_export_text` | Write the reading-order text of pages to a . |
| `pdfcraft_doc_flatten` | Merge comment and/or form field appearances into the page content, so they print and display everywhere but can no longer be edited. |
| `pdfcraft_doc_header_footer` | Add a header and/or footer to pages. |
| `pdfcraft_doc_hidden_info` | What Remove Hidden Information would remove, by category (metadata, attachments, comments, form-fields, hidden-text, hidden-layers, bookmarks, links-actions-scripts, private-data) with counts. |
| `pdfcraft_doc_import_data` | Import comments and/or field values from an XFDF, FDF, XML, CSV or tab-delimited text file (detected from its content), or the comments of another PDF, each onto the page with the same number (comments on pages past this document's last page are left out). |
| `pdfcraft_doc_info` | Metadata, page sizes and labels, bookmarks, annotations, form fields, links, layers, page transitions and display times, the destination it opens at, attachments, fonts, security and repair notes. |
| `pdfcraft_doc_initial_view` | Read or change how the document opens (Document Properties ▸ Initial View) and its reading options: navigation (page, bookmarks, pages, attachments, layers), layout (default, single, continuous, two_up, two_up_continuous, two_up_cover, two_up_continuous_cover), magnification (default, actual, fit_page, fit_width, fit_height, fit_visible, or a percentage), page, window options (fit_window, center_window, full_screen, display_title), interface options (hide_menubar, hide_toolbar, hide_window_ui), language and binding (left, right). |
| `pdfcraft_doc_inspect` | With doc, return doc_info; otherwise return information for every open document (empty documents array when none are open). |
| `pdfcraft_doc_list` | List the open documents with their ids, page counts and unsaved state. |
| `pdfcraft_doc_open` | Open a PDF file and return its document id, page count and whether it can be edited. |
| `pdfcraft_doc_open_revision` | Open saved revision `revision` (1 = the oldest) of a document as a new, unsaved document, to see the file as it was then. |
| `pdfcraft_doc_optimize` | Write an optimized copy to `path` (Acrobat's PDF Optimizer). |
| `pdfcraft_doc_print` | Print with Acrobat's Print dialog options, or save the print-ready PDF. |
| `pdfcraft_doc_protect` | Encrypt the document (applied by the next doc_save, a full rewrite). |
| `pdfcraft_doc_reduce` | Write a smaller copy of the document to `path` with Acrobat's Reduce File Size choices: colour and grey images above 225 ppi downsampled to 150 ppi and JPEG-compressed (medium quality), black-and-white images averaged down to 300 ppi above 450 ppi and each stored as CCITT Group 4 (or 1-bit Flate, once resampled or packed from more bits) whenever that is smaller, thumbnails dropped, identical fonts and images merged, unused objects dropped, compressed object streams. |
| `pdfcraft_doc_remove_hidden` | Remove the listed categories (see doc_hidden_info), or every category when none are listed (Sanitize Document). |
| `pdfcraft_doc_remove_marks` | Remove every header and footer, watermark or background PdfCraft (or a compatible tool) added. |
| `pdfcraft_doc_revisions` | List the document's saved revisions (oldest first): each incremental update is one. |
| `pdfcraft_doc_save` | Save to its own file (an incremental update, which keeps signatures valid) or to a new path (a full rewrite). |
| `pdfcraft_doc_set_info` | Set a document information entry such as Title, Author, Subject or Keywords, or a custom property under any other name (no spaces, delimiters, / or #; at most 127 bytes; doc_info lists them under custom); an empty value removes it. |
| `pdfcraft_doc_split` | Split into several files written to out_dir: every N pages, before given pages, at top-level bookmarks (bookmarks: true; files named after them, repeated titles get -2, -3), or by file size (max_mb). |
| `pdfcraft_doc_unprotect` | Remove password security (the document must have been opened with its permissions password, or have none). |
| `pdfcraft_doc_watermark` | Add a watermark to pages: text, or a picture from `file` (an image, or page `file_page` of a PDF) at `scale` of the page (default 0. |
| `pdfcraft_edit_redo` | Redo the last undone edit of a document. |
| `pdfcraft_edit_undo` | Undo the last edit of a document. |
| `pdfcraft_fill_sign_add` | Fill in a form that has no fields, as Acrobat's Fill & Sign does: type text (`text`, default 10 pt; `font_size` 4–300 pt; optional `color` as #RRGGBB for text/date, default black), place a check, cross, dot or line, today's date (in Preferences ▸ Date format, see fill_sign_date_format, or `format`; `font_size` also applies), or a signature or initials (either `text` drawn in a script font, or `path` to a local PNG/JPEG image up to 4 MiB and 32 megapixels, scaled down to 4 megapixels, preserving transparency; with `scan: true`, `path` is instead a photo of a signature on paper, within the same limits: the signature is found, and the paper, shadows and table around it are removed, with `sensitivity` 0–100, default 50, picking up fainter ink when higher). |
| `pdfcraft_fill_sign_date_format` | Preferences ▸ Date format: the pattern Fill & Sign dates use (default m/d/yyyy). |
| `pdfcraft_form_actions` | Field Properties ▸ Actions: the field's action for each trigger (mouse_up, mouse_down, mouse_enter, mouse_exit, on_focus, on_blur). |
| `pdfcraft_form_add_field` | Add a form field on a page. |
| `pdfcraft_form_add_field_table` | Divide rect into rows and columns of text fields, one per cell, as one undo step. |
| `pdfcraft_form_calculation_order` | The calculated fields in the order they calculate (Acrobat: Set Field Calculation Order), each with its `formula` (as form_fields shows calculate), the fields it reads (`reads`; a script's names built at run time aren't known) and its `issues`: missing_field (it reads `field`, which the form doesn't have, so it gets no value there), runs_too_early (it reads `field`, which calculates after it, so it shows a stale value), cycle (it reads `fields`, which read it back: no order fixes that, a formula has to change) and not_in_order (the PDF's order leaves it out, so other viewers may not calculate it) and built_names (its script also reads fields by names it builds at run time, which aren't checked). |
| `pdfcraft_form_delete_field` | Delete a form field and all its widgets, or with widget only that one: one radio button of a group (widget n is the nth of the radio group's options in form_fields), or one copy of a duplicated field. |
| `pdfcraft_form_detect_fields` | Prepare a form ▸ automatic field detection: find the blanks a printed form asks to be filled (underscore runs, lines, empty boxes, rows of comb boxes, small squares for check boxes; on scanned pages read from the pixels) and name each field from its label. |
| `pdfcraft_form_fields` | Every interactive form field: name, type (text, checkbox, radio, combo, list, button, signature), value, options, page, rect (top-left-origin points) and rotation (0, 90, 180 or 270 degrees counterclockwise), read-only and required flags. |
| `pdfcraft_form_fill` | Set several fields at once (one undo step). |
| `pdfcraft_form_merge_data` | Collect the field values of form data files (FDF, XFDF) or filled-in PDF forms into one CSV file at path: a column per field name, a row per file. |
| `pdfcraft_form_reset` | Reset fields to their default values: all of them, or only those listed. |
| `pdfcraft_form_set_actions` | Field Properties ▸ Actions: replace the field's actions. |
| `pdfcraft_form_set_image` | Show an image file (PNG, JPEG, TIFF, GIF or BMP) in an image field or button, scaled to fit and centred (what clicking an image field does). |
| `pdfcraft_form_set_props` | Change field properties: give field for one field, or fields for a list of unique field names (1–1000). |
| `pdfcraft_form_set_script` | Field Properties ▸ Run custom script: set field's JavaScript for event keystroke, format, validate or calculate (the field's actions; calculated fields join the calculation order) or mouse_up (a button's action). |
| `pdfcraft_form_tab_order` | Set the tab order of pages (default all): row (top to bottom, left to right; right to left in a document bound on the right), column, structure, or annotations (unspecified). |
| `pdfcraft_image_edit` | Change one of a page's images (number from page_images): action move (rect: new full placement box in top-left-origin points, based on page_images. |
| `pdfcraft_image_hit` | List image/Form numbers whose placement and all clipping paths contain point [x,y] in top-left-origin points. |
| `pdfcraft_image_save` | Write one of a page's raster images (number from page_images; forms are refused) to path: JPEG images unchanged, others as PNG (the extension is added when missing). |
| `pdfcraft_js_document_scripts` | List the document-level JavaScripts (name and source), which define functions field scripts use. |
| `pdfcraft_js_enabled` | Preferences ▸ JavaScript ▸ Enable Acrobat JavaScript: set it with `enabled`, or read it. |
| `pdfcraft_js_run` | Run Acrobat JavaScript in the document, as the JavaScript console does (or as push button `field`'s Mouse Up script when field is given; on a laid-out XFA form, `field` runs that button's XFA click script instead, JavaScript or FormCalc, which can add and remove rows and show or hide subforms). |
| `pdfcraft_js_set_document_script` | Add or replace the document-level JavaScript `name` with `script`, or delete it (script omitted). |
| `pdfcraft_layer_set` | Show or hide a layer (optional content group), as the Layers panel's eye icon does. |
| `pdfcraft_link_add` | Add a link over rect on page that opens url or goes to to_page. |
| `pdfcraft_link_delete` | Delete one link (page, index from link_list). |
| `pdfcraft_link_edit` | Change a link's rect, destination (url or to_page) or appearance. |
| `pdfcraft_link_list` | Every link: page, 1-based index (for link_edit/link_delete), rect (points from the top-left of the page), and where it goes (url or to_page). |
| `pdfcraft_link_open` | Follow a local GoToR link in PdfCraft: open the referenced PDF as a new document, respecting --root. |
| `pdfcraft_links_from_urls` | Find web addresses (http://, https://, www. |
| `pdfcraft_links_remove` | Remove every link in the document (or on the given pages). |
| `pdfcraft_measure_area` | Add an undoable area annotation from a simple polygon. |
| `pdfcraft_measure_distance` | Add an undoable two-point distance annotation using the scale of the first point's viewport. |
| `pdfcraft_measure_export` | Atomically write saved measurement values, labels, authors and scale ratios as spreadsheet-safe CSV. |
| `pdfcraft_measure_info` | Calculate a live distance, perimeter or area, deltas, angle and scale without adding an annotation. |
| `pdfcraft_measure_list` | Saved measurement annotations with calculated values, scale and vertices in display coordinates. |
| `pdfcraft_measure_perimeter` | Add an undoable connected-line length annotation. |
| `pdfcraft_measure_scale` | Read the scale at a point, or add a rectangular viewport using a ratio (page_distance in page_unit on the page = distance in unit, e. |
| `pdfcraft_measure_snap` | Snap a point to vector paths, endpoints, midpoints or intersections. |
| `pdfcraft_object_list` | List existing paragraphs, Image/Form artwork and added content once, with source kind/index references, displayed rectangles and document generation. |
| `pdfcraft_object_move` | Atomically translate 1–1000 mixed references from object_list by [dx, dy] in displayed points (right/down). |
| `pdfcraft_ocr_recognize` | Scan & OCR ▸ Recognize text: render pages, read the words in them and add them as invisible text over the page image, so scanned pages become searchable and selectable (a searchable image; the image is not changed). |
| `pdfcraft_ocr_recognize_files` | Scan & OCR ▸ Recognize text ▸ In multiple files: read every page of each PDF in paths and write the searchable result into folder under the same name (pages that already have text are left alone unless skip_text_pages is false, as in ocr_recognize). |
| `pdfcraft_ocr_status` | Whether text recognition is available (its models are installed: release packages include them; a source build fetches them with `cargo xtask models`; PDFCRAFT_MODELS overrides), where it looks for them, and the languages it reads. |
| `pdfcraft_page_add_image` | Add an image file (PNG, JPEG, TIFF, GIF, BMP) as page content: in rect (points from the top-left of the page), or centred at its natural size (shrunk to fit). |
| `pdfcraft_page_add_text` | Add text as page content (not a comment). |
| `pdfcraft_page_delete` | Delete pages. |
| `pdfcraft_page_duplicate` | Insert copies of pages so the first copy becomes page `at`, or after the last of them when `at` is left out (fonts and images are shared, not copied). |
| `pdfcraft_page_enhance_camera` | Straighten a photographed document (Scan & OCR ▸ Enhance ▸ Camera image): the part of the page inside the four corners (x1, y1, … x4, y4 in top-left-origin points, any order, a convex quadrilateral; when omitted, the document's edges are found automatically, or an error says they could not be) is warped to an upright rectangle that replaces what the page shows, at the page picture's own resolution (at most 600 dpi). |
| `pdfcraft_page_extract` | Copy pages into a new PDF (links, bookmarks, fields and layers that belong to them come along). |
| `pdfcraft_page_images` | The raster images and grouped Form artwork a page draws (Edit a PDF): number, full placement rect and visible_rect after page/path clipping (top-left-origin points; null if fully hidden), kind (image/form), pixel size ([0,0] for forms) and resource name. |
| `pdfcraft_page_insert_blank` | Insert a blank page so it becomes page `at`. |
| `pdfcraft_page_insert_file` | Insert pages of another PDF so the first becomes page `at`. |
| `pdfcraft_page_move` | Move pages so the first of them lands at position `to` (1-based, counted before the move). |
| `pdfcraft_page_number` | Label a range of pages (e. |
| `pdfcraft_page_render` | Render one page to a PNG image (default 96 dpi, at most 600). |
| `pdfcraft_page_replace` | Replace the content of pages with pages of another PDF (same count). |
| `pdfcraft_page_reverse` | Reverse the order of pages among the positions they occupy: the listed pages (at least two), or the whole document when pages is omitted. |
| `pdfcraft_page_rotate` | Rotate pages by a multiple of 90 degrees (positive is clockwise): the listed pages (default all), filtered like Acrobat's Rotate Pages by subset (all, even, odd page numbers) and orientation (all, landscape, portrait). |
| `pdfcraft_page_set_box` | Set a page box (crop by default; also trim, bleed, art, media) on pages: either margins in points from the media box [left, bottom, right, top], or an absolute rect in points from the top-left of the displayed page. |
| `pdfcraft_page_transition_set` | Set or remove the transition and display time pages play in a full-screen presentation (ISO 32000-2 §12. |
| `pdfcraft_pdfa_convert` | Standards ▸ Save as PDF/A: fix what can be fixed for PDF/A-2b or 3b (XMP identification and metadata, an sRGB output intent, forbidden actions and JavaScript, annotation print flags, image interpolation, encryption). |
| `pdfcraft_pdfa_verify` | Standards ▸ Verify PDF/A compliance: the PDF/A-2b or 3b rules the document breaks (ISO 19005 clause, message, page, whether Save as PDF/A can fix it), plus what it declares. |
| `pdfcraft_print_readiness` | Verification only. |
| `pdfcraft_printer_options` | A printer driver's own job options (CUPS: from its PPD), such as the paper tray, paper type or finishing: key, label, group, default and choices. |
| `pdfcraft_printers` | The printers the system's print spooler knows (CUPS on macOS and Linux), with the default marked. |
| `pdfcraft_redact_apply` | Apply the redaction marks (all, or those on pages): text, images, vectors, comments and form fields under them are removed for good and boxes are drawn in their place. |
| `pdfcraft_redact_clear` | Remove every redaction mark without applying it. |
| `pdfcraft_redact_mark` | Mark content for redaction (nothing is removed until redact_apply). |
| `pdfcraft_render_preview` | Render a PNG bounded by max_side (default 1024), without changing or saving the document. |
| `pdfcraft_sign_document` | Sign with a digital ID (a . |
| `pdfcraft_sign_id_create` | Create a self-signed digital ID and save it as a password-protected . |
| `pdfcraft_sign_keychain_ids` | macOS: the signing identities in the user's keychains (certificate details and the keychain: reference sign_document takes). |
| `pdfcraft_sign_list` | Every signature field with its validation: status (valid, unknown = intact but the signer isn't trusted, invalid, unsigned), signer and certificate, date, reason, location, certification level, page and rect, the revision it covers and changes made after signing (none, allowed, disallowed), with Acrobat-style explanations. |
| `pdfcraft_sign_trust` | Add certificates (. |
| `pdfcraft_sign_windows_ids` | Windows: signing identities in the Current User Personal certificate store (certificate details and the windows: reference sign_document takes). |
| `pdfcraft_stamp_custom` | Stamp a picture: a PDF page (file_page, default 1, kept as vector content in a form XObject) or an image file. |
| `pdfcraft_standards_remove_id` | Remove what identifies the document as PDF/A (its pdfaid: XMP properties) or PDF/X (GTS_PDFXVersion and GTS_PDFXConformance, in the document information and as pdfxid: XMP properties), e. |
| `pdfcraft_text_edit` | Replace the text of one paragraph (paragraph, from text_paragraphs: rewrapped to the paragraph's width with its line spacing) or one line (line, from text_lines) in place, keeping position, size and colour. |
| `pdfcraft_text_edit_layout` | Measure a paragraph draft using the same PDF rewrite as Apply, without changing the document. |
| `pdfcraft_text_extract` | Extract the text of some or all pages, in reading order. |
| `pdfcraft_text_find` | Find a phrase (case-insensitive, whitespace-normalised) and return matches in page order with page and line rectangles in points (origin top-left). |
| `pdfcraft_text_font_files` | Discover openly licensed, embeddable TrueType/OpenType files on request. |
| `pdfcraft_text_font_import` | Load an explicitly selected, openly licensed full TrueType/OpenType face into a page. |
| `pdfcraft_text_fonts` | List validated embedded source faces and approved full preview faces for a page. |
| `pdfcraft_text_lines` | The lines of existing text on a page (Edit a PDF ▸ Edit text): number, text, box (top-left-origin points), font and size. |
| `pdfcraft_text_paragraphs` | The paragraphs on a page (adjacent source runs grouped into aligned visual rows, including mixed fonts, sizes and colours): number, text, editor_text (visual rows separated by newlines), rows and source line numbers, box (top-left-origin points), font and size. |
| `pdfcraft_text_script` | Format text ▸ Superscript or Subscript on one paragraph (paragraph, from text_paragraphs), or on range [start, end): UTF-8 byte offsets of its editor_text. |
| `pdfcraft_text_styles` | The styles the document's text is set in, the largest first: font (without its subset tag), the size it is shown at in points, bold, italic, how many lines and pages use it, and the first line in it as a sample. |
| `pdfcraft_text_word_count` | Count Unicode words and characters on selected pages (default all), with totals and per-page counts. |
| `pdfcraft_view_reading_colors` | Set the document's reading colours (Acrobat's Replace Document Colors, in the Reading Options): solid text and line-art paints are remapped for readability and the page clears to the background colour in page_render. |
| `pdfcraft_xfa_to_static` | Make an XFA form an ordinary PDF form: the XFA packets (template, data, scripts) and PdfCraft's private keys go; the pages as laid out and the fields with their values stay, so every viewer shows the same form and none lays it out again. |

## Functionalities

- `pdfcraft-edit_pdf` — Inspect a PDF, run engine commands on it and check the render.
- `pdfcraft-fill_form` — Detect, fill and reset the fields of a PDF form.
- `pdfcraft-redact_document` — Mark, apply and audit redactions in a document.
- `pdfcraft-extract_content` — Extract text and pages from a document.
- `pdfcraft-add_bookmarks` — Build and adjust the bookmark outline of a document.
- `pdfcraft-recognize_scans` — Run OCR on scanned pages and read the recognized text.
