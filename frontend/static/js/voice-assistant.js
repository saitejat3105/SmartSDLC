let isRecording = false;
let recognition = null;
let speechSynthesis = window.speechSynthesis;

// Initialize Speech Recognition
if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'en-US';

    recognition.onresult = async (event) => {
        const transcript = event.results[0][0].transcript;
        document.getElementById('voiceOutput').innerHTML = `<p><strong>You:</strong> ${transcript}</p><p>Processing...</p>`;

        try {
            // Get response from Gemini
            const response = await fetch('/api/voice-assistant', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ text: transcript })
            });

            const data = await response.json();
            const assistantResponse = data.response;

            // Display response
            document.getElementById('voiceOutput').innerHTML = `
                <p><strong>You:</strong> ${transcript}</p>
                <p><strong>Assistant:</strong> ${assistantResponse}</p>
            `;

            // Speak the response
            speakText(assistantResponse);

        } catch (error) {
            document.getElementById('voiceOutput').innerHTML = `
                <p><strong>You:</strong> ${transcript}</p>
                <p style="color: var(--danger);"><strong>Error:</strong> Could not get response</p>
            `;
        }

        stopRecording();
    };

    recognition.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        document.getElementById('voiceOutput').innerHTML += `<p style="color: var(--danger);">Error: ${event.error}</p>`;
        stopRecording();
    };

    recognition.onend = () => {
        stopRecording();
    };
}

function toggleVoiceAssistant() {
    const voiceWindow = document.getElementById('voiceWindow');
    voiceWindow.classList.toggle('active');
}

function startRecording() {
    if (!recognition) {
        alert('Speech recognition is not supported in your browser. Please use Chrome or Edge.');
        return;
    }

    if (isRecording) {
        stopRecording();
        return;
    }

    isRecording = true;
    const voiceBtn = document.getElementById('voiceBtn');
    const startBtn = document.getElementById('startRecording');
    
    voiceBtn.classList.add('recording');
    startBtn.textContent = 'Stop Recording';
    startBtn.classList.remove('btn-primary');
    startBtn.classList.add('btn-danger');

    document.getElementById('voiceOutput').innerHTML = '<p style="color: var(--primary);">🎤 Listening... Speak now!</p>';

    try {
        recognition.start();
    } catch (error) {
        console.error('Error starting recognition:', error);
        stopRecording();
    }
}

function stopRecording() {
    isRecording = false;
    const voiceBtn = document.getElementById('voiceBtn');
    const startBtn = document.getElementById('startRecording');
    
    voiceBtn.classList.remove('recording');
    startBtn.textContent = 'Start Recording';
    startBtn.classList.remove('btn-danger');
    startBtn.classList.add('btn-primary');

    if (recognition) {
        try {
            recognition.stop();
        } catch (error) {
            console.error('Error stopping recognition:', error);
        }
    }
}

function speakText(text) {
    // Cancel any ongoing speech
    speechSynthesis.cancel();

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 0.9;
    utterance.pitch = 1;
    utterance.volume = 1;
    
    // Use a more natural voice if available
    const voices = speechSynthesis.getVoices();
    const englishVoice = voices.find(voice => voice.lang.startsWith('en-')) || voices[0];
    if (englishVoice) {
        utterance.voice = englishVoice;
    }

    utterance.onend = () => {
        console.log('Speech finished');
    };

    utterance.onerror = (event) => {
        console.error('Speech error:', event.error);
    };

    speechSynthesis.speak(utterance);
}

// Load voices when they become available
if (speechSynthesis.onvoiceschanged !== undefined) {
    speechSynthesis.onvoiceschanged = () => {
        speechSynthesis.getVoices();
    };
}