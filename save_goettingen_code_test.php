<?php

$code = $_POST['completion_code'] ?? null;

if (!$code) {
    echo "ERROR: Missing completion code.";
    exit;
}

$base_path = "data_test";   // Match your existing data structure
$file = $base_path . "/completion_codes_goettingen.txt";

// Create directory if missing
if (!is_dir($base_path)) {
    mkdir($base_path, 0777, true);
}

// Append code without any identifiers
$line = $code . "\n";

if (file_put_contents($file, $line, FILE_APPEND | LOCK_EX) === false) {
    echo "ERROR: Could not save code.";
    exit;
}

echo "SUCCESS";

?>
