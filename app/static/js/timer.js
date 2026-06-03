// app/static/js/timer.js
// 錄音秒錶計時器控制

window.RecordingTimer = (function() {
    let startTime = 0;
    let elapsedMs = 0;
    let timerInterval = null;
    let onTickCallback = null;

    function formatTime(totalSeconds) {
        const hrs = Math.floor(totalSeconds / 3600);
        const mins = Math.floor((totalSeconds % 3600) / 60);
        const secs = totalSeconds % 60;
        return [
            hrs.toString().padStart(2, '0'),
            mins.toString().padStart(2, '0'),
            secs.toString().padStart(2, '0')
        ].join(':');
    }

    function updateDisplay() {
        const display = document.getElementById('timer-display');
        if (display) {
            const seconds = Math.floor(elapsedMs / 1000);
            display.textContent = formatTime(seconds);
        }
    }

    return {
        start: function(onTick) {
            if (timerInterval) return;
            startTime = Date.now() - elapsedMs;
            onTickCallback = onTick;
            timerInterval = setInterval(() => {
                elapsedMs = Date.now() - startTime;
                updateDisplay();
                if (onTickCallback) {
                    onTickCallback(Math.floor(elapsedMs / 1000));
                }
            }, 100);
            
            const timerDisplay = document.getElementById('timer-display');
            if (timerDisplay) {
                timerDisplay.className = 'duration-timer recording';
            }
        },
        pause: function() {
            if (!timerInterval) return;
            clearInterval(timerInterval);
            timerInterval = null;
            
            const timerDisplay = document.getElementById('timer-display');
            if (timerDisplay) {
                timerDisplay.className = 'duration-timer paused';
            }
        },
        stop: function() {
            this.pause();
        },
        reset: function() {
            this.pause();
            elapsedMs = 0;
            updateDisplay();
            
            const timerDisplay = document.getElementById('timer-display');
            if (timerDisplay) {
                timerDisplay.className = 'duration-timer';
            }
        },
        getDurationSeconds: function() {
            return Math.floor(elapsedMs / 1000);
        }
    };
})();
