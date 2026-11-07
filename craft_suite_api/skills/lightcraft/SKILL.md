---
name: lightcraft
description: LightCraft photo library and raw development — imports, queries, develop settings and exports.
---

# Lightcraft

## When to use

LightCraft photo library and raw development — imports, queries, develop settings and exports.

## Activation

Call `registry_activate` with the namespace `lightcraft` before using any `lightcraft_*` tool.

## Files in and out

Pass an input file as `exchange://<sink>/<key>` (for example `exchange://files/in/photo.png`) or as an `https` URL; the server stages it and hands the app a local path. Give an output path as a relative path such as `out.png`: it lands in this run's folder, and after the call the result links each output in every configured sink.

## When the app is not ready

An app is `warming` while its command registry loads, `Ready` when it serves, `Degraded` after a failed load and `Backoff` once its retries are used. A call to a `warming` app answers the retryable refusal `APP_WARMING`; a call to a `Degraded` or `Backoff` app answers the retryable refusal `APP_REGISTRY_UNREADABLE`. Retry after `retry_after_s`; a `Backoff` app needs an operator.

## Tools

| Tool | What it does |
|---|---|
| `lightcraft_apply_preset` | Apply a develop preset (ids from cmd_presets_list) to the selection or `ids`, at `amount` percent (0. |
| `lightcraft_cmd_activity_cancel` | Cancel Background Task (command `activity. |
| `lightcraft_cmd_activity_list` | Background Tasks (command `activity. |
| `lightcraft_cmd_album_addPhotos` | Add to Album (command `album. |
| `lightcraft_cmd_album_clearQuick` | Clear Quick Collection (command `album. |
| `lightcraft_cmd_album_create` | New Album (command `album. |
| `lightcraft_cmd_album_createSmart` | New Smart Album… (command `album. |
| `lightcraft_cmd_album_delete` | Delete Album (command `album. |
| `lightcraft_cmd_album_move` | Move Album (command `album. |
| `lightcraft_cmd_album_removePhotos` | Remove from Album (command `album. |
| `lightcraft_cmd_album_rename` | Rename Album (command `album. |
| `lightcraft_cmd_album_reorder` | Reorder Album (command `album. |
| `lightcraft_cmd_album_ruleFields` | Smart Album Rule Fields (command `album. |
| `lightcraft_cmd_album_setCover` | Set as Album Cover (command `album. |
| `lightcraft_cmd_album_setRules` | Edit Smart Album (command `album. |
| `lightcraft_cmd_album_setTarget` | Set as Target Album (command `album. |
| `lightcraft_cmd_album_sort` | Sort Albums by Name (command `album. |
| `lightcraft_cmd_album_toggleTarget` | Add to Target Album (command `album. |
| `lightcraft_cmd_albums_list` | List Albums (command `albums. |
| `lightcraft_cmd_app_export` | Export Now (command `app. |
| `lightcraft_cmd_app_gpu` | GPU Rendering (command `app. |
| `lightcraft_cmd_app_memoryBudget` | Memory Budget (command `app. |
| `lightcraft_cmd_beforeAfter_copyAfterToBefore` | Copy After's Settings to Before (command `beforeAfter. |
| `lightcraft_cmd_beforeAfter_copyBeforeToAfter` | Copy Before's Settings to After (command `beforeAfter. |
| `lightcraft_cmd_beforeAfter_resetBefore` | Reset Before to Import State (command `beforeAfter. |
| `lightcraft_cmd_beforeAfter_setBefore` | Set Before (command `beforeAfter. |
| `lightcraft_cmd_beforeAfter_swap` | Swap Before and After Settings (command `beforeAfter. |
| `lightcraft_cmd_catalog_query` | Query Photos (command `catalog. |
| `lightcraft_cmd_catalog_stats` | Catalog Statistics (command `catalog. |
| `lightcraft_cmd_crop_aspect` | Crop Aspect (command `crop. |
| `lightcraft_cmd_crop_autoStraighten` | Auto Straighten (command `crop. |
| `lightcraft_cmd_crop_drag` | Drag Crop Handle (command `crop. |
| `lightcraft_cmd_crop_reset` | Reset Crop (command `crop. |
| `lightcraft_cmd_crop_rotateAspect` | Rotate Crop Aspect (command `crop. |
| `lightcraft_cmd_crop_set` | Set Crop (command `crop. |
| `lightcraft_cmd_crop_straighten` | Straighten (command `crop. |
| `lightcraft_cmd_curve_applyPreset` | Apply Point Curve Preset (command `curve. |
| `lightcraft_cmd_curve_deletePreset` | Delete Point Curve Preset (command `curve. |
| `lightcraft_cmd_curve_exportPresets` | Export Point Curve Presets (command `curve. |
| `lightcraft_cmd_curve_importPresets` | Import Point Curve Presets (command `curve. |
| `lightcraft_cmd_curve_presets` | Point Curve Presets (command `curve. |
| `lightcraft_cmd_curve_reset` | Reset Tone Curve (command `curve. |
| `lightcraft_cmd_curve_savePreset` | Save Point Curve Preset (command `curve. |
| `lightcraft_cmd_denoise_cancel` | Cancel Denoise (command `denoise. |
| `lightcraft_cmd_denoise_clear` | Clear Denoise Cache (command `denoise. |
| `lightcraft_cmd_denoise_models_download` | Download Denoise Model (command `denoise. |
| `lightcraft_cmd_denoise_models_downloadCancel` | Cancel Denoise Model Download (command `denoise. |
| `lightcraft_cmd_denoise_models_downloads` | Denoise Model Downloads (command `denoise. |
| `lightcraft_cmd_denoise_models_inspect` | Inspect Denoise Model (command `denoise. |
| `lightcraft_cmd_denoise_models_install` | Install Denoise Model (command `denoise. |
| `lightcraft_cmd_denoise_models_list` | Denoise Models (command `denoise. |
| `lightcraft_cmd_denoise_models_remove` | Remove Denoise Model (command `denoise. |
| `lightcraft_cmd_denoise_models_select` | Choose Denoise Model (command `denoise. |
| `lightcraft_cmd_denoise_models_test` | Test Denoise Model (command `denoise. |
| `lightcraft_cmd_denoise_pump` | Denoise Pump (command `denoise. |
| `lightcraft_cmd_denoise_queue` | Denoise Photos (command `denoise. |
| `lightcraft_cmd_denoise_settings` | Denoise Settings (command `denoise. |
| `lightcraft_cmd_denoise_status` | Denoise Status (command `denoise. |
| `lightcraft_cmd_denoise_toggle` | AI Denoise (command `denoise. |
| `lightcraft_cmd_develop_adjust` | Nudge Develop Value (command `develop. |
| `lightcraft_cmd_develop_auto` | Auto Settings (command `develop. |
| `lightcraft_cmd_develop_autoBwMix` | Auto B&W Mix (command `develop. |
| `lightcraft_cmd_develop_autoSync` | Auto Sync (command `develop. |
| `lightcraft_cmd_develop_beginInteraction` | Begin Interaction (command `develop. |
| `lightcraft_cmd_develop_cancelInteraction` | Cancel Interaction (command `develop. |
| `lightcraft_cmd_develop_controls` | List Develop Controls (command `develop. |
| `lightcraft_cmd_develop_copy` | Copy Edit Settings (command `develop. |
| `lightcraft_cmd_develop_curve` | Set Point Curve (command `develop. |
| `lightcraft_cmd_develop_endInteraction` | End Interaction (command `develop. |
| `lightcraft_cmd_develop_get` | Get Develop Settings (command `develop. |
| `lightcraft_cmd_develop_hdr` | HDR (command `develop. |
| `lightcraft_cmd_develop_matchExposure` | Match Total Exposures (command `develop. |
| `lightcraft_cmd_develop_merge` | Apply Settings JSON (command `develop. |
| `lightcraft_cmd_develop_paste` | Paste Edit Settings (command `develop. |
| `lightcraft_cmd_develop_pastePrevious` | Paste Settings from Previous (command `develop. |
| `lightcraft_cmd_develop_profile` | Set Profile (command `develop. |
| `lightcraft_cmd_develop_quickAdjust` | Quick Develop (command `develop. |
| `lightcraft_cmd_develop_reset` | Reset Edits (command `develop. |
| `lightcraft_cmd_develop_resetControl` | Reset Control (command `develop. |
| `lightcraft_cmd_develop_resetSection` | Reset Section (command `develop. |
| `lightcraft_cmd_develop_sectionEnabled` | Toggle Section (command `develop. |
| `lightcraft_cmd_develop_set` | Set Develop Values (command `develop. |
| `lightcraft_cmd_develop_sync` | Sync Settings (command `develop. |
| `lightcraft_cmd_develop_targeted` | Targeted Adjustment (command `develop. |
| `lightcraft_cmd_develop_treatment` | Black & White (command `develop. |
| `lightcraft_cmd_develop_updateProcess` | Update to Current Process (command `develop. |
| `lightcraft_cmd_develop_wb` | White Balance (command `develop. |
| `lightcraft_cmd_develop_wbPick` | White Balance Selector (command `develop. |
| `lightcraft_cmd_edit_redo` | Redo (command `edit. |
| `lightcraft_cmd_edit_undo` | Undo (command `edit. |
| `lightcraft_cmd_export_addToPhotos` | Add to Apple Photos (command `export. |
| `lightcraft_cmd_export_checkTarget` | Check Output Path (command `export. |
| `lightcraft_cmd_export_contactSheet` | Export Contact Sheet PDF (command `export. |
| `lightcraft_cmd_export_deletePreset` | Delete Export Preset (command `export. |
| `lightcraft_cmd_export_photosImports` | Apple Photos Imports (command `export. |
| `lightcraft_cmd_export_presets` | Export Presets (command `export. |
| `lightcraft_cmd_export_savePreset` | Save Export Preset (command `export. |
| `lightcraft_cmd_faces_detect` | Detect Faces (command `faces. |
| `lightcraft_cmd_faces_enable` | Face Recognition On/Off (command `faces. |
| `lightcraft_cmd_faces_evaluate` | Evaluate Face Recognition (command `faces. |
| `lightcraft_cmd_faces_gpu` | Face Models on the GPU (command `faces. |
| `lightcraft_cmd_faces_index` | Index Faces (command `faces. |
| `lightcraft_cmd_faces_models_download` | Download Face Model (command `faces. |
| `lightcraft_cmd_faces_models_downloadCancel` | Cancel Face Model Download (command `faces. |
| `lightcraft_cmd_faces_models_downloads` | Face Model Downloads (command `faces. |
| `lightcraft_cmd_faces_models_inspect` | Inspect Face Model File (command `faces. |
| `lightcraft_cmd_faces_models_install` | Install Face Model (command `faces. |
| `lightcraft_cmd_faces_models_list` | Face Models (command `faces. |
| `lightcraft_cmd_faces_models_remove` | Remove Face Model (command `faces. |
| `lightcraft_cmd_faces_models_select` | Choose Face Recognition Model (command `faces. |
| `lightcraft_cmd_faces_models_test` | Test Face Model (command `faces. |
| `lightcraft_cmd_faces_nameFaces` | Name Faces (command `faces. |
| `lightcraft_cmd_faces_person` | Faces of a Person (command `faces. |
| `lightcraft_cmd_faces_pump` | Index Faces in the Background (command `faces. |
| `lightcraft_cmd_faces_renamePerson` | Rename Person (command `faces. |
| `lightcraft_cmd_faces_setName` | Name Face (command `faces. |
| `lightcraft_cmd_faces_suggest` | Suggest Names for Faces (command `faces. |
| `lightcraft_cmd_faces_unnamed` | Unnamed Faces (command `faces. |
| `lightcraft_cmd_filter_applyPreset` | Apply Filter Preset (command `filter. |
| `lightcraft_cmd_filter_deletePreset` | Delete Filter Preset (command `filter. |
| `lightcraft_cmd_filter_presets` | Filter Presets (command `filter. |
| `lightcraft_cmd_filter_savePreset` | Save Filter Preset (command `filter. |
| `lightcraft_cmd_focus_pump` | Read Focus Points in the Background (command `focus. |
| `lightcraft_cmd_folder_create` | New Folder on Disk (command `folder. |
| `lightcraft_cmd_folder_label` | Set Folder Color Label (command `folder. |
| `lightcraft_cmd_folder_move` | Move Folder (command `folder. |
| `lightcraft_cmd_folder_rename` | Rename Folder (command `folder. |
| `lightcraft_cmd_folder_scanChanges` | Scan Folder for Changes (command `folder. |
| `lightcraft_cmd_folder_synchronize` | Synchronize Folder (command `folder. |
| `lightcraft_cmd_geometry_guides` | Guided Upright Guides (command `geometry. |
| `lightcraft_cmd_geometry_upright` | Upright (command `geometry. |
| `lightcraft_cmd_history_clear` | Clear History (command `history. |
| `lightcraft_cmd_history_list` | List History (command `history. |
| `lightcraft_cmd_history_next` | Next History Step (command `history. |
| `lightcraft_cmd_history_previous` | Previous History Step (command `history. |
| `lightcraft_cmd_history_restore` | Go to History Step (command `history. |
| `lightcraft_cmd_journal_list` | Command Journal (command `journal. |
| `lightcraft_cmd_keyword_create` | Create Keyword (command `keyword. |
| `lightcraft_cmd_keyword_delete` | Delete Keyword (command `keyword. |
| `lightcraft_cmd_keyword_deleteSet` | Delete Keyword Set (command `keyword. |
| `lightcraft_cmd_keyword_edit` | Edit Keyword (command `keyword. |
| `lightcraft_cmd_keyword_export` | Export Keywords (command `keyword. |
| `lightcraft_cmd_keyword_import` | Import Keywords (command `keyword. |
| `lightcraft_cmd_keyword_info` | Keyword Info (command `keyword. |
| `lightcraft_cmd_keyword_list` | Keywords (command `keyword. |
| `lightcraft_cmd_keyword_merge` | Merge Keywords (command `keyword. |
| `lightcraft_cmd_keyword_move` | Move Keyword (command `keyword. |
| `lightcraft_cmd_keyword_nextSet` | Next Keyword Set (command `keyword. |
| `lightcraft_cmd_keyword_previousSet` | Previous Keyword Set (command `keyword. |
| `lightcraft_cmd_keyword_purgeUnused` | Purge Unused Keywords (command `keyword. |
| `lightcraft_cmd_keyword_rename` | Rename Keyword (command `keyword. |
| `lightcraft_cmd_keyword_saveSet` | Save Keyword Set (command `keyword. |
| `lightcraft_cmd_keyword_setDefaultParent` | Put New Keywords Inside (command `keyword. |
| `lightcraft_cmd_keyword_setShortcut` | Set Keyword Shortcut (command `keyword. |
| `lightcraft_cmd_keyword_sets` | Keyword Sets (command `keyword. |
| `lightcraft_cmd_keyword_shortcut` | Keyword Shortcut (command `keyword. |
| `lightcraft_cmd_keyword_suggest` | Keyword Suggestions (command `keyword. |
| `lightcraft_cmd_keyword_toggleFromSet` | Toggle Keyword from Set (command `keyword. |
| `lightcraft_cmd_keyword_toggleShortcut` | Add or Remove Keyword Shortcut (command `keyword. |
| `lightcraft_cmd_keyword_useSet` | Use Keyword Set (command `keyword. |
| `lightcraft_cmd_label_applySet` | Apply Color Label Set (command `label. |
| `lightcraft_cmd_label_deleteSet` | Delete Color Label Set (command `label. |
| `lightcraft_cmd_label_names` | Color Label Names (command `label. |
| `lightcraft_cmd_label_saveSet` | Save Color Label Set (command `label. |
| `lightcraft_cmd_label_setNames` | Edit Color Label Names (command `label. |
| `lightcraft_cmd_label_sets` | Color Label Sets (command `label. |
| `lightcraft_cmd_lens_databaseStatus` | Lens Database Status (command `lens. |
| `lightcraft_cmd_lens_downloadDatabase` | Download the Lens Database (command `lens. |
| `lightcraft_cmd_library_autoImport` | Auto Import Settings (command `library. |
| `lightcraft_cmd_library_autoImportScan` | Auto Import Now (command `library. |
| `lightcraft_cmd_library_browse` | Browse Folder (command `library. |
| `lightcraft_cmd_library_buildPreviews` | Build Previews (command `library. |
| `lightcraft_cmd_library_cancelPreviews` | Cancel Preview Build (command `library. |
| `lightcraft_cmd_library_clearFilter` | Clear Filters (command `library. |
| `lightcraft_cmd_library_clearPreviews` | Discard Preview Cache (command `library. |
| `lightcraft_cmd_library_compact` | Optimize Library (command `library. |
| `lightcraft_cmd_library_devices` | Cameras and Cards (command `library. |
| `lightcraft_cmd_library_down` | Photo Below (command `library. |
| `lightcraft_cmd_library_emptyRecentlyDeleted` | Empty Recently Deleted (command `library. |
| `lightcraft_cmd_library_filter` | Filter (command `library. |
| `lightcraft_cmd_library_findMissing` | Find Missing Photos (command `library. |
| `lightcraft_cmd_library_findSimilar` | Find Similar Photos (command `library. |
| `lightcraft_cmd_library_folders` | Library Folders (command `library. |
| `lightcraft_cmd_library_forgetLocal` | Forget Unchanged Local Photos (command `library. |
| `lightcraft_cmd_library_groups` | Date Groups (command `library. |
| `lightcraft_cmd_library_holdView` | Hold View Until Refreshed (command `library. |
| `lightcraft_cmd_library_import` | Import Photos (command `library. |
| `lightcraft_cmd_library_importLightroom` | Import Lightroom Catalog (command `library. |
| `lightcraft_cmd_library_importPreview` | Review Import (command `library. |
| `lightcraft_cmd_library_info` | Library Info (command `library. |
| `lightcraft_cmd_library_inspectLightroom` | Inspect Lightroom Catalog (command `library. |
| `lightcraft_cmd_library_memory` | Memory Usage (command `library. |
| `lightcraft_cmd_library_missing` | Missing Photos (command `library. |
| `lightcraft_cmd_library_next` | Next Photo (command `library. |
| `lightcraft_cmd_library_preferences` | Library Preferences (command `library. |
| `lightcraft_cmd_library_previewProgress` | Preview Build Progress (command `library. |
| `lightcraft_cmd_library_previous` | Previous Photo (command `library. |
| `lightcraft_cmd_library_recheckPreviewOnly` | Recheck Preview-Only Raws (command `library. |
| `lightcraft_cmd_library_refresh` | Refresh View (command `library. |
| `lightcraft_cmd_library_refreshLensProfiles` | Look Up Lens Profiles Again (command `library. |
| `lightcraft_cmd_library_removeFolder` | Remove Folder from Library (command `library. |
| `lightcraft_cmd_library_retrySidecars` | Write Waiting XMP Sidecars (command `library. |
| `lightcraft_cmd_library_select` | Select Photos (command `library. |
| `lightcraft_cmd_library_selectAll` | Select All (command `library. |
| `lightcraft_cmd_library_selectBy` | Select by Flag, Rating or Label (command `library. |
| `lightcraft_cmd_library_selectNone` | Deselect All (command `library. |
| `lightcraft_cmd_library_shuffle` | Reshuffle (command `library. |
| `lightcraft_cmd_library_smartPreviews` | Build Smart Previews (command `library. |
| `lightcraft_cmd_library_smartPreviewsLocation` | Smart Previews Location (command `library. |
| `lightcraft_cmd_library_sort` | Sort (command `library. |
| `lightcraft_cmd_library_source` | Show Source (command `library. |
| `lightcraft_cmd_library_state` | Library State (command `library. |
| `lightcraft_cmd_library_toggleAutoWriteXmp` | Automatically Write Changes into XMP (command `library. |
| `lightcraft_cmd_library_toggleFilters` | Enable Filters (command `library. |
| `lightcraft_cmd_library_up` | Photo Above (command `library. |
| `lightcraft_cmd_library_xmpPreferences` | XMP Sidecar Preferences (command `library. |
| `lightcraft_cmd_mask_add` | Create New Mask (command `mask. |
| `lightcraft_cmd_mask_addComponent` | Add/Subtract/Intersect Mask (command `mask. |
| `lightcraft_cmd_mask_adjust` | Set Mask Adjustments (command `mask. |
| `lightcraft_cmd_mask_applyEffect` | Apply Mask Effect (command `mask. |
| `lightcraft_cmd_mask_brushStroke` | Brush Stroke (command `mask. |
| `lightcraft_cmd_mask_component` | Edit Mask Component (command `mask. |
| `lightcraft_cmd_mask_delete` | Delete Mask (command `mask. |
| `lightcraft_cmd_mask_deleteAll` | Delete All Masks (command `mask. |
| `lightcraft_cmd_mask_deleteEffect` | Delete Mask Effect (command `mask. |
| `lightcraft_cmd_mask_duplicate` | Duplicate Mask (command `mask. |
| `lightcraft_cmd_mask_duplicateEffect` | Duplicate Mask Effect (command `mask. |
| `lightcraft_cmd_mask_effects` | Mask Effect Presets (command `mask. |
| `lightcraft_cmd_mask_exportEffects` | Export Mask Effects (command `mask. |
| `lightcraft_cmd_mask_favoriteEffect` | Favorite Mask Effect (command `mask. |
| `lightcraft_cmd_mask_importEffects` | Import Mask Effects (command `mask. |
| `lightcraft_cmd_mask_invert` | Invert Mask (command `mask. |
| `lightcraft_cmd_mask_move` | Move Mask (command `mask. |
| `lightcraft_cmd_mask_objectPoint` | Add Object Click (command `mask. |
| `lightcraft_cmd_mask_refine` | Refine Mask Edges (command `mask. |
| `lightcraft_cmd_mask_refineDetail` | Refine AI Mask Detail (command `mask. |
| `lightcraft_cmd_mask_rename` | Rename Mask (command `mask. |
| `lightcraft_cmd_mask_renameEffect` | Rename Mask Effect (command `mask. |
| `lightcraft_cmd_mask_renameEffectGroup` | Rename Mask Effect Group (command `mask. |
| `lightcraft_cmd_mask_sampleColor` | Sample Mask Color (command `mask. |
| `lightcraft_cmd_mask_saveEffect` | Save Mask Effect (command `mask. |
| `lightcraft_cmd_mask_select` | Select Mask (command `mask. |
| `lightcraft_cmd_mask_setEffectGroup` | Move Mask Effect to Group (command `mask. |
| `lightcraft_cmd_mask_toolEffect` | Set Effect for New Masks (command `mask. |
| `lightcraft_cmd_mask_update` | Update Mask Shape (command `mask. |
| `lightcraft_cmd_mask_updateEffect` | Update Mask Effect (command `mask. |
| `lightcraft_cmd_mask_visible` | Show/Hide Mask (command `mask. |
| `lightcraft_cmd_merge_hdr` | HDR Merge (command `merge. |
| `lightcraft_cmd_merge_hdrBatch` | HDR for Each Bracket Set (command `merge. |
| `lightcraft_cmd_merge_hdrPanorama` | HDR Panorama Merge (command `merge. |
| `lightcraft_cmd_merge_panorama` | Panorama Merge (command `merge. |
| `lightcraft_cmd_metadata_applyPreset` | Apply Metadata Preset (command `metadata. |
| `lightcraft_cmd_metadata_deletePreset` | Delete Metadata Preset (command `metadata. |
| `lightcraft_cmd_metadata_downloadPlaceNames` | Download Place Names (GeoNames) (command `metadata. |
| `lightcraft_cmd_metadata_placeNamesStatus` | Place Names Status (command `metadata. |
| `lightcraft_cmd_metadata_presets` | Metadata Presets (command `metadata. |
| `lightcraft_cmd_metadata_reverseGeocode` | Fill Location from GPS (command `metadata. |
| `lightcraft_cmd_metadata_savePreset` | Save Metadata Preset (command `metadata. |
| `lightcraft_cmd_photo_addToLibrary` | Add to My Photos (command `photo. |
| `lightcraft_cmd_photo_allMetadata` | All Metadata (command `photo. |
| `lightcraft_cmd_photo_analyze` | Assisted Culling (command `photo. |
| `lightcraft_cmd_photo_autoTagTracklog` | Auto-Tag Photos from Tracklog (command `photo. |
| `lightcraft_cmd_photo_clearLabel` | Clear Color Label (command `photo. |
| `lightcraft_cmd_photo_convertToDng` | Convert to DNG (command `photo. |
| `lightcraft_cmd_photo_copyMetadata` | Copy Metadata (command `photo. |
| `lightcraft_cmd_photo_cycleFlag` | Cycle Flag (command `photo. |
| `lightcraft_cmd_photo_decreaseFlag` | Decrease Flag Status (command `photo. |
| `lightcraft_cmd_photo_decreaseRating` | Decrease Rating (command `photo. |
| `lightcraft_cmd_photo_delete` | Delete Photo (command `photo. |
| `lightcraft_cmd_photo_deletePermanently` | Delete Permanently (command `photo. |
| `lightcraft_cmd_photo_duplicate` | Duplicate (command `photo. |
| `lightcraft_cmd_photo_editExternal` | Edit Copy for External Editor (command `photo. |
| `lightcraft_cmd_photo_flag` | Set Flag (command `photo. |
| `lightcraft_cmd_photo_flipHorizontal` | Flip Horizontal (command `photo. |
| `lightcraft_cmd_photo_flipVertical` | Flip Vertical (command `photo. |
| `lightcraft_cmd_photo_increaseFlag` | Increase Flag Status (command `photo. |
| `lightcraft_cmd_photo_increaseRating` | Increase Rating (command `photo. |
| `lightcraft_cmd_photo_inspect` | Inspect Photo (command `photo. |
| `lightcraft_cmd_photo_label` | Set Color Label (command `photo. |
| `lightcraft_cmd_photo_moveToFolder` | Move to Folder (command `photo. |
| `lightcraft_cmd_photo_pasteMetadata` | Paste Metadata (command `photo. |
| `lightcraft_cmd_photo_pick` | Flag as Pick (command `photo. |
| `lightcraft_cmd_photo_rate` | Set Rating (command `photo. |
| `lightcraft_cmd_photo_readFocusPoints` | Read Focus Points (command `photo. |
| `lightcraft_cmd_photo_readMetadataFromFile` | Read Metadata from File (command `photo. |
| `lightcraft_cmd_photo_reject` | Flag as Reject (command `photo. |
| `lightcraft_cmd_photo_relink` | Locate Photo (command `photo. |
| `lightcraft_cmd_photo_reload` | Reload from Disk (command `photo. |
| `lightcraft_cmd_photo_removeRegion` | Remove Face Box (command `photo. |
| `lightcraft_cmd_photo_rename` | Rename Photos (command `photo. |
| `lightcraft_cmd_photo_renamePreview` | Rename Preview (command `photo. |
| `lightcraft_cmd_photo_renameTokens` | Rename Template Tags (command `photo. |
| `lightcraft_cmd_photo_restore` | Restore (command `photo. |
| `lightcraft_cmd_photo_rotateLeft` | Rotate Left (command `photo. |
| `lightcraft_cmd_photo_rotateRight` | Rotate Right (command `photo. |
| `lightcraft_cmd_photo_saveMetadataToFile` | Save Metadata to File (command `photo. |
| `lightcraft_cmd_photo_setCaptureTime` | Edit Capture Time (command `photo. |
| `lightcraft_cmd_photo_setMeta` | Edit Info (command `photo. |
| `lightcraft_cmd_photo_setRegion` | Resize Face Box (command `photo. |
| `lightcraft_cmd_photo_smartPreview` | Smart Preview Status (command `photo. |
| `lightcraft_cmd_photo_unflag` | Unflag (command `photo. |
| `lightcraft_cmd_photo_virtualCopy` | Create Virtual Copy (command `photo. |
| `lightcraft_cmd_pointColor_delete` | Delete Point Color Sample (command `pointColor. |
| `lightcraft_cmd_pointColor_pick` | Add Point Color Sample (command `pointColor. |
| `lightcraft_cmd_preset_apply` | Apply Preset (command `preset. |
| `lightcraft_cmd_preset_create` | Create Preset (command `preset. |
| `lightcraft_cmd_preset_delete` | Delete Preset (command `preset. |
| `lightcraft_cmd_preset_export` | Export Presets (command `preset. |
| `lightcraft_cmd_preset_favorite` | Favorite Preset (command `preset. |
| `lightcraft_cmd_preset_import` | Import Presets (command `preset. |
| `lightcraft_cmd_preset_move` | Move Preset to Group (command `preset. |
| `lightcraft_cmd_preset_rename` | Rename Preset (command `preset. |
| `lightcraft_cmd_preset_update` | Update Preset with Current Settings (command `preset. |
| `lightcraft_cmd_presets_list` | List Presets (command `presets. |
| `lightcraft_cmd_print_cell_add` | Add Print Cell (command `print. |
| `lightcraft_cmd_print_cell_delete` | Delete Print Cell (command `print. |
| `lightcraft_cmd_print_cell_move` | Move Print Cell (command `print. |
| `lightcraft_cmd_print_cell_page` | Move Print Cell to Page (command `print. |
| `lightcraft_cmd_print_cell_photo` | Set Print Cell Photo (command `print. |
| `lightcraft_cmd_print_cell_resize` | Resize Print Cell (command `print. |
| `lightcraft_cmd_print_cell_stack` | Arrange Print Cell (command `print. |
| `lightcraft_cmd_print_exportPdf` | Print to PDF (command `print. |
| `lightcraft_cmd_print_get` | Print Settings (command `print. |
| `lightcraft_cmd_print_layout_autoLayout` | Auto Layout (command `print. |
| `lightcraft_cmd_print_layout_clear` | Clear Print Layout (command `print. |
| `lightcraft_cmd_print_layout_newPage` | New Print Page (command `print. |
| `lightcraft_cmd_print_reset` | Reset Print Settings (command `print. |
| `lightcraft_cmd_print_set` | Set Print Settings (command `print. |
| `lightcraft_cmd_print_template_apply` | Apply Print Template (command `print. |
| `lightcraft_cmd_print_template_delete` | Delete Print Template (command `print. |
| `lightcraft_cmd_print_template_export` | Export Print Template (command `print. |
| `lightcraft_cmd_print_template_import` | Import Print Template (command `print. |
| `lightcraft_cmd_print_template_list` | Print Templates (command `print. |
| `lightcraft_cmd_print_template_save` | Save Print Template (command `print. |
| `lightcraft_cmd_profile_deleteImported` | Delete Imported Profile (command `profile. |
| `lightcraft_cmd_profile_favorite` | Favorite Profile (command `profile. |
| `lightcraft_cmd_profile_import` | Import Profiles (command `profile. |
| `lightcraft_cmd_profiles_list` | List Profiles (command `profiles. |
| `lightcraft_cmd_profiles_menu` | Profile Menu (command `profiles. |
| `lightcraft_cmd_redeye_add` | Add Red Eye Correction (command `redeye. |
| `lightcraft_cmd_redeye_catchlight` | Pet Eye Catchlight (command `redeye. |
| `lightcraft_cmd_redeye_delete` | Delete Red Eye Correction (command `redeye. |
| `lightcraft_cmd_segment_model_cancel` | Cancel AI Mask Model Download (command `segment. |
| `lightcraft_cmd_segment_model_download` | Download AI Mask Model (command `segment. |
| `lightcraft_cmd_segment_model_status` | AI Mask Model Status (command `segment. |
| `lightcraft_cmd_segment_prepare` | Prepare AI Masks (command `segment. |
| `lightcraft_cmd_slideshow_export` | Export Slideshow (command `slideshow. |
| `lightcraft_cmd_slideshow_exportStatus` | Slideshow Export Status (command `slideshow. |
| `lightcraft_cmd_slideshow_layout` | Slideshow Layout Settings (command `slideshow. |
| `lightcraft_cmd_slideshow_overlays` | Slideshow Overlay Settings (command `slideshow. |
| `lightcraft_cmd_slideshow_playback` | Slideshow Playback Settings (command `slideshow. |
| `lightcraft_cmd_slideshow_preview` | Slideshow Slide Preview (command `slideshow. |
| `lightcraft_cmd_slideshow_templates_apply` | Apply Slideshow Template (command `slideshow. |
| `lightcraft_cmd_slideshow_templates_delete` | Delete Slideshow Template (command `slideshow. |
| `lightcraft_cmd_slideshow_templates_export` | Export Slideshow Template (command `slideshow. |
| `lightcraft_cmd_slideshow_templates_import` | Import Slideshow Template (command `slideshow. |
| `lightcraft_cmd_slideshow_templates_list` | Slideshow Templates (command `slideshow. |
| `lightcraft_cmd_slideshow_templates_rename` | Rename Slideshow Template (command `slideshow. |
| `lightcraft_cmd_slideshow_templates_save` | Save Slideshow Template (command `slideshow. |
| `lightcraft_cmd_slideshow_templates_update` | Update Slideshow Template (command `slideshow. |
| `lightcraft_cmd_slideshow_titles` | Slideshow Title Settings (command `slideshow. |
| `lightcraft_cmd_spot_add` | Add Remove Spot (command `spot. |
| `lightcraft_cmd_spot_delete` | Delete Spot (command `spot. |
| `lightcraft_cmd_spot_findBlemishes` | Find Blemishes (command `spot. |
| `lightcraft_cmd_spot_findDust` | Find Dust Spots (command `spot. |
| `lightcraft_cmd_spot_refreshSource` | Refresh Source (command `spot. |
| `lightcraft_cmd_spot_select` | Select Spot (command `spot. |
| `lightcraft_cmd_spot_update` | Edit Spot (command `spot. |
| `lightcraft_cmd_stack_auto` | Auto-Stack by Capture Time (command `stack. |
| `lightcraft_cmd_stack_collapseAll` | Collapse All Stacks (command `stack. |
| `lightcraft_cmd_stack_expandAll` | Expand All Stacks (command `stack. |
| `lightcraft_cmd_stack_group` | Group into Stack (command `stack. |
| `lightcraft_cmd_stack_moveDown` | Move Down in Stack (command `stack. |
| `lightcraft_cmd_stack_moveUp` | Move Up in Stack (command `stack. |
| `lightcraft_cmd_stack_remove` | Remove from Stack (command `stack. |
| `lightcraft_cmd_stack_setTop` | Set as Top of Stack (command `stack. |
| `lightcraft_cmd_stack_split` | Split Stack (command `stack. |
| `lightcraft_cmd_stack_toggle` | Expand/Collapse Stack (command `stack. |
| `lightcraft_cmd_stack_ungroup` | Ungroup Stack (command `stack. |
| `lightcraft_cmd_version_create` | Create Version (command `version. |
| `lightcraft_cmd_version_delete` | Delete Version (command `version. |
| `lightcraft_cmd_version_rename` | Rename Version (command `version. |
| `lightcraft_cmd_version_restore` | Restore Version (command `version. |
| `lightcraft_cmd_version_update` | Update Version with Current Settings (command `version. |
| `lightcraft_command_batch` | Run several commands in order: {steps: [{id, params? |
| `lightcraft_command_list` | Every command (engine + UI when connected) with id, label, menu, shortcut, parameter doc and whether it is enabled now. |
| `lightcraft_command_run` | Run any LightCraft command by id with JSON params (see command_list for ids and parameter docs), e. |
| `lightcraft_crop` | Set the crop of the active photo: `rect` [x0,y0,x1,y1] in normalized coordinates (0. |
| `lightcraft_doc_inspect` | The library as JSON: current source, filter, sort, selection, active photo and undo/redo labels (library. |
| `lightcraft_export` | Render and write photos. |
| `lightcraft_get_develop` | The full develop settings JSON of a photo (white balance, light, color, curves, mixer, grading, effects, crop, masks, spots…). |
| `lightcraft_import` | Add image/raw files to the library. |
| `lightcraft_list_commands` | Every command (engine + UI when connected) with id, label, menu, shortcut, parameter doc and whether it is enabled now. |
| `lightcraft_list_controls` | Every develop slider (id like `light. |
| `lightcraft_query_photos` | List photos (id, file name, size, rating, flag, edited…). |
| `lightcraft_render_photo` | Render a photo with its current develop settings (cropped) and return it as an image so you can look at the result. |
| `lightcraft_render_preview` | Render a photo with its current develop settings (cropped) and return it as an image (`max_side` is the long edge; does not change selection or save a file). |
| `lightcraft_run_command` | Run any LightCraft command by id with JSON params (see list_commands for ids and parameter docs), e. |
| `lightcraft_select_photos` | Set the selection; the active photo (the one develop tools edit) is `active` or the first id. |
| `lightcraft_set_develop` | Edit a photo (one undo step each for values and settings). |

## Functionalities

- `lightcraft-develop_photo` — Import a photo, adjust its develop settings and export it.
- `lightcraft-query_library` — Find and select photos in the library.
- `lightcraft-run_commands` — Look up engine commands and run them.
