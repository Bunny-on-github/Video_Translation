// main.js
document.getElementById('video-upload').onchange = function(e) {
    // Show video preview when the file is uploaded
    const videoPreview = document.getElementById('video-preview');
    videoPreview.src = URL.createObjectURL(e.target.files[0]);
    videoPreview.style.display = "block";
};

document.getElementById('upload-form').onsubmit = async function(e) {
    e.preventDefault();  // Prevent the default form submission behavior

    let formData = new FormData(this);

    // Show a status update
    document.getElementById('status').textContent = "Processing... Please wait.";

    try {
        const response = await fetch('/process_video', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        // Update status, transcription, translation
        document.getElementById('status').textContent = result.status;
        document.getElementById('transcription').textContent = result.transcription;
        document.getElementById('translation').textContent = result.translation;

        // Add download links for audio files
        const extractedAudio = document.getElementById('extracted-audio');
        extractedAudio.href = '/audio/extracted_audio.wav';
        extractedAudio.textContent = "Download Extracted Audio";

        const translatedAudio = document.getElementById('translated-audio');
        translatedAudio.href = '/translated_audio/translated_audio.mp3';
        translatedAudio.textContent = "Download Translated Audio";

        // Add download link for processed video
        const outputVideo = document.getElementById('output-video');
        outputVideo.href = '/' + result.output_video;
        outputVideo.textContent = "Download Processed Video";

    } catch (error) {
        console.error("Error occurred:", error);
        document.getElementById('status').textContent = "An error occurred during processing.";
    }
};
