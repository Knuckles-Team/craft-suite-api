---
name: photocraft-edit-product-photo
description: Open a product photo, crop and resize it for a listing, lift exposure and saturation, add a headline, and export PNG and JPEG.
---

# Edit a product photo

## When to use

A product shot needs to become a listing, ad or social image: reframe it, correct exposure or colour, and put a short headline on it.

## Inputs

- `${photo}`: the source photo, as exchange://<sink>/<key> or an https URL.
- `${headline}`: the headline text.

Every app tool is served by the craft-suite-api connector; call them in this order in one session (the app keeps the open document between calls). A value written `${name}` is an input above or the value an earlier step returned (its answer names it).

## Steps

| # | Tool | Arguments | Why |
|---|---|---|---|
| 1 | `photocraft_doc_open` | `{"path": "${photo}"}` | Open the photo; the answer gives its width and height. |
| 2 | `photocraft_cmd_image_crop` | `{"x": 200, "y": 150, "width": 1200, "height": 900}` | Crop to the product (pixels from the top-left). |
| 3 | `photocraft_cmd_image_imageSize` | `{"width": 1080, "height": 810}` | Resize to the delivery size. |
| 4 | `photocraft_cmd_image_adjustments_exposure` | `{"exposure": 0.6}` | Lift the exposure (EV stops, -20..20). |
| 5 | `photocraft_cmd_image_adjustments_hueSaturation` | `{"saturation": 30}` | Raise the saturation (-100..100). |
| 6 | `photocraft_cmd_type_create` | `{"x": 60, "y": 740, "text": "${headline}", "size": 64, "color": "#ffffff", "font": "DejaVu Sans"}` | Add the headline as a text layer (x,y is the baseline start; size in pt; color #rrggbb). |
| 7 | `photocraft_cmd_layer_flattenImage` | `{}` | Flatten so the exports carry the text. |
| 8 | `photocraft_doc_export` | `{"path": "product-edit.png"}` | Export a PNG; a relative path lands in the run folder and is published. |
| 9 | `photocraft_doc_export` | `{"path": "product-edit.jpg"}` | Export a JPEG copy the same way. |
| 10 | `photocraft_doc_close` | `{}` | Close the document so the session holds nothing stale. |

## Outputs

Formats: png, jpg. A relative output path lands in the run folder of the call; after the call the result's `scion/artifacts` lists each file with its link in every configured exchange sink (the object store under `<app>/<date>/<run>/<name>`, and the file share when configured). Pass a published file to another workflow as `exchange://objects/<key>`.

## Verify

Open the exported files: the size equals the resize target, the colours are brighter and more saturated than the crop of the source, and the headline pixels are present.

## Notes

- Export with `photocraft_doc_export`; path-taking engine commands such as `file.saveACopy` are disabled under automation and refuse.
- `photocraft_cmd_type_create` takes character keys (font, size, color) next to x, y and text; its schema leaves them open, so pass them as documented.

## Refusals

`APP_WARMING` (retryable, `retry_after_s`): the app's command registry is still loading after a restart; wait and call again. `APP_REGISTRY_UNREADABLE` (retryable): the app's registry could not be read; it is retried in the background. Report any other refusal verbatim; never retry past it.
