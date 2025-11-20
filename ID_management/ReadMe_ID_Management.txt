Participant ID Management – Overview

The script generates a unique numeric participant identifier (ID) by querying the server via a synchronous AJAX POST request. This ID is then used to:

    Determine which stimuli subset to assign to the participant.

    Generate unique filenames for saving their data.

🔧 Technical Details
1. The getID() function

This function is defined to contact a server-side PHP file (manageID.php) and retrieve a numeric participant ID:

function getID(url, datDir) {
  let numID = 0;
  $.ajax({
    url: url,
    type: 'POST',
    async: false, // synchronous request (blocking)
    data: { dir: datDir }, // data sent to the server
  }).done(function (data) {
    numID = data;
  });
  return numID;
}

    url: The endpoint of the server-side script (manageID.php)

    datDir: (currently unused in your call) could be used to specify a directory where data is stored

    async: false: Ensures that the experiment pauses until an ID is returned (important to prevent proceeding before ID is known)

2. Calling getID()

The ID is requested early in the script:

ID = getID("manageID.php");

3. Using the ID

Once retrieved, the ID is used to:
a. Assign a specific subset of stimuli:

const items_per_participant = 10;
const start_index = (ID - 1) * items_per_participant;
const end_index = start_index + items_per_participant;
const participant_stimuli = stimulus_list.slice(start_index, end_index);

This ensures each participant gets a unique set of items, without overlap (assuming enough stimuli are available).
b. Handle error if insufficient stimuli:

if (end_index > stimulus_list.length) {
  alert("Nicht genug Stimuli für diese Teilnehmernummer.");
}

c. Check if ID is valid:

function isEmpty(str) {
  return (!str || str.length === 0);
}

if (isEmpty(ID)) {
  var empty = {
    type: 'html-button-response',
    stimulus: '<p>Leider ist die Datenerhebung für diese Version der Studie bereits abgeschlossen.</p>',
    choices: ['OK']
  };
  timeline.push(empty);
}

d. Generate unique filenames for saving data:

const filename = `ger_lex_proj_p${subject_id}_block${block_counter}_${timestamp}.csv`;

Although subject_id is randomly generated, the ID from the server determines the stimuli assigned — you could choose to use ID instead of subject_id for filename consistency, or combine both.