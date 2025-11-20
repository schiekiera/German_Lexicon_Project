<?php

// Get POST parameters
$folder   = $_POST['folder'] ?? null;   // university parameter
$filename = $_POST['filename'] ?? null;
$filedata = $_POST['filedata'] ?? null;

// Basic validation
if (!$folder || !$filename || !$filedata) {
    echo "ERROR: Missing parameters.";
    exit;
}

$base_path = "data";                    // main data directory
$target_dir = $base_path . "/" . $folder;

// Create base folder if missing
if (!is_dir($base_path)) {
    mkdir($base_path, 0777, true);
}

// Create university folder if missing (data/<uni>)
if (!is_dir($target_dir)) {
    if (!mkdir($target_dir, 0777, true)) {
        echo "ERROR: Failed to create directory: $target_dir";
        exit;
    }
}

// Full path to save main data file
$filepath = $target_dir . "/" . $filename;

// -----------------------------------------
// (A) SAVE MAIN DATA FILE
// -----------------------------------------
if (file_put_contents($filepath, $filedata) === false) {
    echo "ERROR: Could not save data file.";
    exit;
}

// -----------------------------------------
// (B) ALSO SAVE EMPTY PROGRESS MARKER FILE
// -----------------------------------------
$progress_base = "data_collection_progress";
$progress_dir  = $progress_base . "/" . $folder;

// Create main progress directory if missing
if (!is_dir($progress_base)) {
    mkdir($progress_base, 0777, true);
}

// Create progress subfolder for this university
if (!is_dir($progress_dir)) {
    mkdir($progress_dir, 0777, true);
}

// Create empty marker file with the SAME name (*.txt)
$marker_filename = $filename . ".txt";
$marker_path = $progress_dir . "/" . $marker_filename;

// Save empty file
file_put_contents($marker_path, "");

// -----------------------------------------

echo "SUCCESS: Saved $filename and progress file.";

?>
