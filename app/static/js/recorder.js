// app/static/js/recorder.js
// 錄音核心控制邏輯與介面互動

document.addEventListener('DOMContentLoaded', function() {
    const startBtn = document.getElementById('start-btn');
    const pauseBtn = document.getElementById('pause-btn');
    const stopBtn = document.getElementById('stop-btn');
    const recordingStatus = document.getElementById('recording-status');
    const markerBtns = document.querySelectorAll('.marker-btn');
    
    // Modal elements
    const saveModal = document.getElementById('save-modal');
    const titleInput = document.getElementById('title-input');
    const durationInput = document.getElementById('duration-sec-input');
    const discardBtn = document.getElementById('discard-btn');
    const audioFileInput = document.getElementById('audio-file-input');

    let mediaRecorder = null;
    let audioStream = null;
    let audioChunks = [];
    let isRecording = false;
    let isPaused = false;

    // Initialize Waveform Canvas
    const canvas = document.getElementById('waveform');
    if (canvas) {
        window.WaveformVisualizer.init(canvas);
    }

    // 開始錄音
    async function startRecording() {
        audioChunks = [];
        window.MarkerManager.clear();
        
        try {
            // 請求麥克風權限
            audioStream = await navigator.mediaDevices.getUserMedia({ audio: true });
            
            // 選擇瀏覽器支援的編碼格式
            let options = { mimeType: 'audio/webm' };
            if (!MediaRecorder.isTypeSupported('audio/webm')) {
                options = { mimeType: 'audio/ogg' };
                if (!MediaRecorder.isTypeSupported('audio/ogg')) {
                    options = {}; // 瀏覽器預設
                }
            }

            mediaRecorder = new MediaRecorder(audioStream, options);
            
            mediaRecorder.ondataavailable = function(e) {
                if (e.data && e.data.size > 0) {
                    audioChunks.push(e.data);
                }
            };

            mediaRecorder.onstop = function() {
                // 將錄製的音訊區塊組合成 Blob
                const mimeType = mediaRecorder.mimeType || 'audio/webm';
                const audioBlob = new Blob(audioChunks, { type: mimeType });
                
                // 取得副檔名
                let ext = '.webm';
                if (mimeType.includes('ogg')) ext = '.ogg';
                else if (mimeType.includes('wav')) ext = '.wav';
                else if (mimeType.includes('mp4')) ext = '.mp4';
                
                // 使用 DataTransfer 將 Blob 包裝成 File 賦值給 file input
                const file = new File([audioBlob], `recording${ext}`, { type: mimeType });
                const dataTransfer = new DataTransfer();
                dataTransfer.items.add(file);
                audioFileInput.files = dataTransfer.files;

                // 停止並釋放所有麥克風軌道
                if (audioStream) {
                    audioStream.getTracks().forEach(track => track.stop());
                }
            };

            // 開始錄製與計時
            mediaRecorder.start(250); // 每 250ms 交付一次數據
            window.RecordingTimer.reset();
            window.RecordingTimer.start();
            window.WaveformVisualizer.start(audioStream);

            isRecording = true;
            isPaused = false;
            
            // 更新按鈕狀態
            startBtn.disabled = true;
            startBtn.classList.add('recording');
            pauseBtn.disabled = false;
            stopBtn.disabled = false;
            recordingStatus.textContent = '正在錄音中...';
            
            // 啟用標記按鈕
            markerBtns.forEach(btn => btn.disabled = false);

        } catch (err) {
            console.error('Error starting recording:', err);
            alert('麥克風啟動失敗！請檢查是否已授權麥克風存取權限。');
            resetUI();
        }
    }

    // 暫停錄音
    function pauseRecording() {
        if (!mediaRecorder || mediaRecorder.state !== 'recording') return;
        
        mediaRecorder.pause();
        window.RecordingTimer.pause();
        window.WaveformVisualizer.pause();
        
        isPaused = true;
        pauseBtn.querySelector('span').textContent = '▶';
        pauseBtn.title = '繼續錄音 (空白鍵)';
        recordingStatus.textContent = '錄音已暫停';
    }

    // 繼續錄音
    function resumeRecording() {
        if (!mediaRecorder || mediaRecorder.state !== 'paused') return;
        
        mediaRecorder.resume();
        window.RecordingTimer.start();
        window.WaveformVisualizer.resume();
        
        isPaused = false;
        pauseBtn.querySelector('span').textContent = '⏸';
        pauseBtn.title = '暫停錄音 (空白鍵)';
        recordingStatus.textContent = '正在錄音中...';
    }

    // 停止錄音
    function stopRecording() {
        if (!mediaRecorder || mediaRecorder.state === 'inactive') return;
        
        mediaRecorder.stop();
        window.RecordingTimer.stop();
        window.WaveformVisualizer.stop();

        const duration = window.RecordingTimer.getDurationSeconds();
        durationInput.value = duration;

        // 預設標題 (當前時間)
        const now = new Date();
        const dateStr = now.getFullYear() +
            '-' + String(now.getMonth() + 1).padStart(2, '0') +
            '-' + String(now.getDate()).padStart(2, '0') +
            ' ' + String(now.getHours()).padStart(2, '0') +
            ':' + String(now.getMinutes()).padStart(2, '0');
        titleInput.value = `錄音 ${dateStr}`;

        // 顯示儲存 Modal
        saveModal.classList.add('active');
    }

    // 放棄錄音並重置
    function discardRecording() {
        if (confirm('確定要放棄此錄音嗎？未儲存的音訊將會丟失。')) {
            saveModal.classList.remove('active');
            resetUI();
            addSystemLog('錄音已放棄');
        }
    }

    function resetUI() {
        isRecording = false;
        isPaused = false;
        
        startBtn.disabled = false;
        startBtn.classList.remove('recording');
        pauseBtn.disabled = true;
        pauseBtn.querySelector('span').textContent = '⏸';
        pauseBtn.title = '暫停錄音 (空白鍵)';
        
        stopBtn.disabled = true;
        recordingStatus.textContent = '準備就緒';
        
        window.RecordingTimer.reset();
        window.WaveformVisualizer.stop();
        window.MarkerManager.clear();
        
        // 停用標記按鈕
        markerBtns.forEach(btn => btn.disabled = true);
        audioFileInput.value = '';
    }

    function addSystemLog(msg) {
        console.log(`[System] ${msg}`);
    }

    // 綁定事件
    startBtn.addEventListener('click', startRecording);
    
    pauseBtn.addEventListener('click', function() {
        if (isPaused) {
            resumeRecording();
        } else {
            pauseRecording();
        }
    });
    
    stopBtn.addEventListener('click', stopRecording);
    discardBtn.addEventListener('click', discardRecording);

    // 標記按鈕點擊事件
    markerBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            if (!isRecording || isPaused) return;

            const typeId = this.getAttribute('data-type-id');
            const color = this.getAttribute('data-color');
            const name = this.querySelector('.name').textContent;
            
            // 立即取得時間戳秒數，防止對話方塊阻礙
            const timeSec = window.RecordingTimer.getDurationSeconds();
            
            // 彈出快速備註輸入框
            const note = prompt(`請輸入「${name}」標記的備註 (非必填)：`, '') || '';
            
            window.MarkerManager.add(typeId, timeSec, note.trim());

            // 標記按鈕點選效果
            this.style.transform = 'scale(0.95)';
            this.style.borderColor = color;
            setTimeout(() => {
                this.style.transform = '';
                this.style.borderColor = '';
            }, 200);
        });
    });

    // 暴露全域控制以便 keyboard.js 存取
    window.RecorderControl = {
        isRecording: () => isRecording,
        isPaused: () => isPaused,
        start: startRecording,
        pause: pauseRecording,
        resume: resumeRecording,
        stop: stopRecording,
        clickMarker: (index) => {
            const btn = document.querySelector(`.marker-btn[data-key="${index}"]`);
            if (btn && !btn.disabled) {
                btn.click();
            }
        }
    };
});
