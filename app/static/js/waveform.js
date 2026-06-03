// app/static/js/waveform.js
// 錄音即時波形視覺化 (Canvas Analyser)

window.WaveformVisualizer = (function() {
    let audioContext = null;
    let analyser = null;
    let dataArray = null;
    let sourceNode = null;
    let animationFrameId = null;
    let canvas = null;
    let canvasCtx = null;
    let isPaused = false;
    let isRecording = false;

    function draw() {
        if (!canvasCtx || !canvas) return;

        animationFrameId = requestAnimationFrame(draw);

        const width = canvas.width;
        const height = canvas.height;

        // Clear canvas with transparent or slightly dark background
        canvasCtx.clearRect(0, 0, width, height);
        canvasCtx.fillStyle = 'rgba(9, 9, 14, 0.2)';
        canvasCtx.fillRect(0, 0, width, height);

        // Draw baseline
        canvasCtx.lineWidth = 2;
        canvasCtx.lineCap = 'round';

        // Gradient for premium aesthetics
        const gradient = canvasCtx.createLinearGradient(0, 0, width, 0);
        gradient.addColorStop(0, '#f43f5e'); // Rose
        gradient.addColorStop(0.5, '#8b5cf6'); // Purple
        gradient.addColorStop(1, '#3b82f6'); // Blue
        canvasCtx.strokeStyle = gradient;

        canvasCtx.beginPath();

        if (!isRecording) {
            // Draw static straight baseline
            canvasCtx.moveTo(0, height / 2);
            canvasCtx.lineTo(width, height / 2);
            canvasCtx.stroke();
            return;
        }

        if (isPaused) {
            // Draw slightly static noisy line or flat line in gray
            canvasCtx.strokeStyle = '#475569'; // Slate Gray
            const bufferLength = 128;
            const sliceWidth = width / bufferLength;
            let x = 0;
            for (let i = 0; i < bufferLength; i++) {
                const y = height / 2 + Math.sin(i * 0.15) * 2; // Subtle sine wave
                if (i === 0) {
                    canvasCtx.moveTo(x, y);
                } else {
                    canvasCtx.lineTo(x, y);
                }
                x += sliceWidth;
            }
            canvasCtx.stroke();
            return;
        }

        // Active recording: draw real audio waveform (time-domain data)
        analyser.getByteTimeDomainData(dataArray);
        const bufferLength = analyser.frequencyBinCount;
        const sliceWidth = width / bufferLength;
        let x = 0;

        for (let i = 0; i < bufferLength; i++) {
            const v = dataArray[i] / 128.0;
            const y = v * (height / 2);

            if (i === 0) {
                canvasCtx.moveTo(x, y);
            } else {
                canvasCtx.lineTo(x, y);
            }

            x += sliceWidth;
        }

        canvasCtx.lineTo(width, height / 2);
        canvasCtx.stroke();
    }

    return {
        init: function(canvasElement) {
            canvas = canvasElement;
            canvasCtx = canvas.getContext('2d');
            
            // Handle DPI scaling
            const rect = canvas.getBoundingClientRect();
            canvas.width = rect.width * window.devicePixelRatio;
            canvas.height = rect.height * window.devicePixelRatio;
            canvasCtx.scale(window.devicePixelRatio, window.devicePixelRatio);
            
            // Draw baseline initially
            isRecording = false;
            isPaused = false;
            draw();
        },
        start: function(stream) {
            if (animationFrameId) {
                cancelAnimationFrame(animationFrameId);
            }

            try {
                audioContext = new (window.AudioContext || window.webkitAudioContext)();
                analyser = audioContext.createAnalyser();
                analyser.fftSize = 256;
                
                sourceNode = audioContext.createMediaStreamSource(stream);
                sourceNode.connect(analyser);

                const bufferLength = analyser.frequencyBinCount;
                dataArray = new Uint8Array(bufferLength);

                isRecording = true;
                isPaused = false;
                draw();
            } catch(e) {
                console.error("Failed to initialize Web Audio API Analyser:", e);
                // Fallback to visual-only simulation
                isRecording = true;
                isPaused = false;
                draw();
            }
        },
        pause: function() {
            isPaused = true;
        },
        resume: function() {
            isPaused = false;
        },
        stop: function() {
            isRecording = false;
            isPaused = false;
            if (animationFrameId) {
                cancelAnimationFrame(animationFrameId);
                animationFrameId = null;
            }
            if (sourceNode) {
                sourceNode.disconnect();
                sourceNode = null;
            }
            if (audioContext && audioContext.state !== 'closed') {
                audioContext.close();
                audioContext = null;
            }
            // Draw static baseline
            draw();
        }
    };
})();
