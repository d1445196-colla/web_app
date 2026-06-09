// app/static/js/waveform.js
// 波形視覺化模組 — 負責使用 Canvas API 與 Web Audio API 渲染音量波形

class WaveformVisualizer {
    constructor(canvasElementId) {
        this.canvas = document.getElementById(canvasElementId);
        if (!this.canvas) return;
        this.ctx = this.canvas.getContext('2d');
        this.audioContext = null;
        this.analyser = null;
        this.dataArray = null;
        this.source = null;
        this.animationId = null;
        this.state = 'idle'; // 'idle', 'recording', 'paused'
        
        // 響應式調整 Canvas 大小
        this.resize();
        window.addEventListener('resize', () => this.resize());
        
        // 用於繪製隨時間向左滾動波形的緩衝陣列
        this.history = new Array(150).fill(0);
    }

    resize() {
        if (!this.canvas) return;
        // 取得容器的寬度
        const rect = this.canvas.parentElement.getBoundingClientRect();
        this.canvas.width = rect.width * (window.devicePixelRatio || 1);
        this.canvas.height = 180 * (window.devicePixelRatio || 1);
        this.canvas.style.width = '100%';
        this.canvas.style.height = '180px';
    }

    init(stream) {
        try {
            const AudioContextClass = window.AudioContext || window.webkitAudioContext;
            this.audioContext = new AudioContextClass();
            this.analyser = this.audioContext.createAnalyser();
            this.analyser.fftSize = 256;
            
            this.source = this.audioContext.createMediaStreamSource(stream);
            this.source.connect(this.analyser);
            
            const bufferLength = this.analyser.frequencyBinCount;
            this.dataArray = new Uint8Array(bufferLength);
        } catch (e) {
            console.error('初始化 Web Audio API 失敗:', e);
        }
    }

    start() {
        this.state = 'recording';
        if (this.audioContext && this.audioContext.state === 'suspended') {
            this.audioContext.resume();
        }
        this.animate();
    }

    pause() {
        this.state = 'paused';
    }

    resume() {
        this.state = 'recording';
        if (this.audioContext && this.audioContext.state === 'suspended') {
            this.audioContext.resume();
        }
    }

    stop() {
        this.state = 'idle';
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
            this.animationId = null;
        }
        this.clearCanvas();
        this.drawIdle();
    }

    cleanup() {
        this.stop();
        if (this.source) {
            this.source.disconnect();
            this.source = null;
        }
        if (this.analyser) {
            this.analyser = null;
        }
        if (this.audioContext) {
            this.audioContext.close();
            this.audioContext = null;
        }
    }

    clearCanvas() {
        if (!this.ctx || !this.canvas) return;
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    }

    animate() {
        if (this.state === 'idle') return;
        
        this.animationId = requestAnimationFrame(() => this.animate());
        this.draw();
    }

    draw() {
        if (!this.ctx || !this.canvas) return;
        
        const width = this.canvas.width;
        const height = this.canvas.height;
        
        this.clearCanvas();
        
        // 取得當前最大音量值（振幅）
        let maxVal = 0;
        if (this.state === 'recording' && this.analyser && this.dataArray) {
            this.analyser.getByteTimeDomainData(this.dataArray);
            
            // 計算最大振幅偏移度
            for (let i = 0; i < this.dataArray.length; i++) {
                const val = Math.abs(this.dataArray[i] - 128);
                if (val > maxVal) {
                    maxVal = val;
                }
            }
        }
        
        // 將最大值對應到 0~1 之間
        const amplitude = Math.min(maxVal / 64.0, 1.0);
        
        // 滾動波形：在 recording 時新增新數據，paused 時新增 0.02 模擬微弱靜止，idle 時全為 0
        if (this.state === 'recording') {
            this.history.push(amplitude);
        } else if (this.state === 'paused') {
            // 暫停時加入極小的波動，呈現靜止但有波紋狀態
            this.history.push(0.01 + Math.sin(Date.now() / 100) * 0.005);
        }
        this.history.shift();
        
        // 繪製波形
        this.ctx.lineWidth = 3;
        this.ctx.lineCap = 'round';
        
        // 漸層色設定 (Rose to Blue)
        const gradient = this.ctx.createLinearGradient(0, 0, width, 0);
        if (this.state === 'recording') {
            gradient.addColorStop(0, '#f43f5e'); // --primary
            gradient.addColorStop(0.5, '#8b5cf6'); // --purple
            gradient.addColorStop(1, '#3b82f6'); // --secondary
            this.ctx.strokeStyle = gradient;
        } else {
            // 暫停時使用灰色
            this.ctx.strokeStyle = '#64748b'; // --text-secondary
        }
        
        this.ctx.beginPath();
        
        const sliceWidth = width / this.history.length;
        let x = 0;
        
        for (let i = 0; i < this.history.length; i++) {
            const amp = this.history[i];
            const waveHeight = amp * (height * 0.7); // 最高佔 70% 高度
            const y = (height / 2) + (Math.sin(i * 0.15) * waveHeight * 0.5); // 上下波動的包絡
            
            // 繪製對稱上下對稱波形條
            const topY = (height / 2) - (waveHeight / 2) - 2;
            const bottomY = (height / 2) + (waveHeight / 2) + 2;
            
            if (i === 0) {
                this.ctx.moveTo(x, height / 2);
            }
            
            this.ctx.moveTo(x, topY);
            this.ctx.lineTo(x, bottomY);
            
            x += sliceWidth;
        }
        
        // 繪製一條中間基準線
        this.ctx.stroke();
        
        // 繪製一條細中央基準線
        this.ctx.beginPath();
        this.ctx.strokeStyle = 'rgba(255, 255, 255, 0.1)';
        this.ctx.lineWidth = 1;
        this.ctx.moveTo(0, height / 2);
        this.ctx.lineTo(width, height / 2);
        this.ctx.stroke();
    }

    drawIdle() {
        if (!this.ctx || !this.canvas) return;
        const width = this.canvas.width;
        const height = this.canvas.height;
        
        this.clearCanvas();
        
        // 繪製靜態水平線
        this.ctx.beginPath();
        this.ctx.strokeStyle = 'rgba(255, 255, 255, 0.15)';
        this.ctx.lineWidth = 2;
        this.ctx.moveTo(0, height / 2);
        this.ctx.lineTo(width, height / 2);
        this.ctx.stroke();
    }
}
