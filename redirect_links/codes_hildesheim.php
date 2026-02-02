<?php
// Get raw POST data
$data = file_get_contents("php://input");

// Decode JSON
$json = json_decode($data, true);
if (!$json || !isset($json['surveyCode'])) {
    http_response_code(400);
    echo "No surveyCode provided";
    exit;
}

$code = intval($json['surveyCode']); // sanitize

// Folder for saving codes
$folder = "participant_codes";
if (!is_dir($folder)) {
    mkdir($folder, 0755, true); // create folder if missing
}

// Prepare line with timestamp
$timestamp = date("Y-m-d H:i:s");
$line = $timestamp . " | " . $code . PHP_EOL;

// Append to local file
$filePath = "$folder/codes_hildesheim.txt";
file_put_contents($filePath, $line, FILE_APPEND | LOCK_EX);

// Send email
$to = "aliona.petrenco@hu-berlin.de"; // <-- change to your email
$subject = "New Participant Code Generated";
$message = "A new participant code was generated:\n\nCode: $code\nTime: $timestamp\nSaved to: $filePath";
$headers = "From: noreply@hu-berlin.de";

$mailSuccess = mail($to, $subject, $message, $headers);

if ($mailSuccess) {
    echo "Saved code: $code at $timestamp and email sent.";
} else {
    echo "Saved code: $code at $timestamp but email failed.";
}
?>
