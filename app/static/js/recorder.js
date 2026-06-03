// app/static/js/recorder.js
// 錄音控制模組 — 負責與 MediaRecorder API 互動，控制錄音生命週期

class AudioRecorder {
    constructor() {
        this.mediaRecorder = null;
        this.stream = null;
        this.chunks = [];
        this.state = 'inactive'; // 'inactive', 'recording', 'paused'
        
        // 回呼函式事件
        this.onStart = null;
        this.onPause = null;
        this.onResume = null;
        this.onStop = null; // 停止時會傳入音訊 Blob
        this.onError = null;
    }

    async start() {
        if (this.state !== 'inactive') return;
        
        try {
            this.stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            
            // 決定支援的音訊 MIME 型態 (WebM 優先)
            let options = { mimeType: 'audio/webm' };
            if (!MediaRecorder.isTypeSupported(options.mimeType)) {
                options = { mimeType: 'audio/ogg' };
                if (!MediaRecorder.isTypeSupported(options.mimeType)) {
                    options = { mimeType: 'audio/mp4' };
                    if (!MediaRecorder.isTypeSupported(options.mimeType)) {
                        options = {}; // 讓瀏覽器決定預設格式
                    }
                }
            }

            this.mediaRecorder = new MediaRecorder(this.stream, options);
            this.chunks = [];

            this.mediaRecorder.ondataavailable = (e) => {
                if (e.data && e.data.size > 0) {
                    this.chunks.push(e.data);
                }
            };

            this.mediaRecorder.onstop = () => {
                const blob = new Blob(this.chunks, { type: this.mediaRecorder.mimeType || 'audio/webm' });
                this.state = 'inactive';
                
                // 停止所有音軌以釋放麥克風資源
                if (this.stream) {
                    this.stream.getTracks().forEach(track => track.stop());
                }

                if (this.onStop) {
                    this.onStop(blob);
                }
            };

            this.mediaRecorder.onerror = (e) => {
                console.error('MediaRecorder 發生錯誤:', e);
                if (this.onError) this.onError(e.error || e);
            };

            this.mediaRecorder.start(1000); // 每秒觸發一次 dataavailable
            this.state = 'recording';
            
            if (this.onStart) {
                this.onStart(this.stream);
            }
        } catch (err) {
            console.error('無法獲取麥克風權限:', err);
            if (this.onError) this.onError(err);
            throw err;
        }
    }

    pause() {
        if (this.state !== 'recording' || !this.mediaRecorder) return;
        this.mediaRecorder.pause();
        this.state = 'paused';
        if (this.onPause) this.onPause();
    }

    resume() {
        if (this.state !== 'paused' || !this.mediaRecorder) return;
        this.mediaRecorder.resume();
        this.state = 'recording';
        if (this.onResume) this.onResume();
    }

    stop() {
        if (this.state === 'inactive' || !this.mediaRecorder) return;
        this.mediaRecorder.stop();
        // 這會觸發 mediaRecorder.onstop
    }
}
