let mediaRecorder;
let audioChunks = [];

document.getElementById('start-recording').addEventListener('click', async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(stream);
    mediaRecorder.ondataavailable = event => {
        audioChunks.push(event.data);
    };
    mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
        const audioUrl = URL.createObjectURL(audioBlob);
        document.getElementById('audio-playback').src = audioUrl;

        // Show loading message
        document.getElementById('loading-message').style.display = 'block';

        // Send audio file to server for processing
        const formData = new FormData();
        formData.append('audio', audioBlob);
        fetch('/process-audio', {
            method: 'POST',
            body: formData
        }).then(response => response.json())
          .then(data => {
              console.log(data);
              
              // Hide loading message
              document.getElementById('loading-message').style.display = 'none';

              // Display the generated video
              const videoOutput = document.getElementById('video-output');
              videoOutput.src = data.video_url;
              videoOutput.style.display = 'block';
          })
          .catch(error => {
              console.error('Error:', error);
              document.getElementById('loading-message').innerText = 'An error occurred. Please try again.';
          });
    };
    mediaRecorder.start();
    document.getElementById('start-recording').disabled = true;
    document.getElementById('stop-recording').disabled = false;
});

document.getElementById('stop-recording').addEventListener('click', () => {
    mediaRecorder.stop();
    document.getElementById('start-recording').disabled = false;
    document.getElementById('stop-recording').disabled = true;
});
