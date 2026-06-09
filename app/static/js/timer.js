// app/static/js/timer.js
// 計時器模組 — 負責錄音計時與格式化顯示

class RecordingTimer {
    constructor(displayElementId) {
        this.displayElement = document.getElementById(displayElementId);
        this.seconds = 0;
        this.intervalId = null;
        this.isRunning = false;
    }

    start() {
        if (this.isRunning) return;
        this.isRunning = true;
        this.intervalId = setInterval(() => {
            this.seconds++;
            this.updateDisplay();
        }, 1000);
        
        if (this.displayElement) {
            this.displayElement.classList.add('recording');
            this.displayElement.classList.remove('paused');
        }
    }

    pause() {
        if (!this.isRunning) return;
        this.isRunning = false;
        clearInterval(this.intervalId);
        this.intervalId = null;
        
        if (this.displayElement) {
            this.displayElement.classList.remove('recording');
            this.displayElement.classList.add('paused');
        }
    }

    resume() {
        this.start();
    }

    stop() {
        this.pause();
    }

    reset() {
        this.stop();
        this.seconds = 0;
        this.updateDisplay();
        if (this.displayElement) {
            this.displayElement.classList.remove('recording', 'paused');
        }
    }

    getSeconds() {
        return this.seconds;
    }

    updateDisplay() {
        if (!this.displayElement) return;
        
        const hrs = Math.floor(this.seconds / 3600);
        const mins = Math.floor((this.seconds % 3600) / 60);
        const secs = this.seconds % 60;
        
        const formatted = [
            hrs.toString().padStart(2, '0'),
            mins.toString().padStart(2, '0'),
            secs.toString().padStart(2, '0')
        ].join(':');
        
        this.displayElement.textContent = formatted;
    }
}
