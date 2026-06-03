// app/static/js/upload.js
// 前端上傳與狀態輪詢控制

document.addEventListener('DOMContentLoaded', function() {
    const dropzone = document.getElementById('dropzone');
    const fileInput = document.getElementById('file-input');
    const fileInfoBox = document.getElementById('file-info-box');
    const fileName = document.getElementById('file-name');
    const fileSize = document.getElementById('file-size');
    const btnRemoveFile = document.getElementById('btn-remove-file');
    const btnSubmit = document.getElementById('btn-submit');
    
    const progressPanel = document.getElementById('progress-panel');
    const statusTitle = document.getElementById('status-title').querySelector('span');
    const percentText = document.getElementById('percent-text');
    const progressBar = document.getElementById('progress-bar');
    const logBox = document.getElementById('log-box');

    let selectedFile = null;
    let pollInterval = null;

    // 格式化檔案大小
    function formatBytes(bytes, decimals = 2) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const dm = decimals < 0 ? 0 : decimals;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
    }

    // 新增日誌
    function addLog(message, type = 'info') {
        const item = document.createElement('div');
        item.className = `log-item ${type}`;
        item.textContent = `[${new Date().toLocaleTimeString()}] ${message}`;
        logBox.appendChild(item);
        logBox.scrollTop = logBox.scrollHeight;
    }

    // 處理選擇檔案
    function handleFile(file) {
        if (!file) return;
        
        // 限制大小 25MB
        if (file.size > 25 * 1024 * 1024) {
            alert('檔案大小不可超過 25MB！');
            resetFile();
            return;
        }

        selectedFile = file;
        fileName.textContent = file.name;
        fileSize.textContent = formatBytes(file.size);
        
        fileInfoBox.style.display = 'flex';
        dropzone.style.display = 'none';
        btnSubmit.disabled = false;
        
        addLog(`已選擇檔案: ${file.name} (${formatBytes(file.size)})`);
    }

    function resetFile() {
        selectedFile = null;
        fileInput.value = '';
        fileInfoBox.style.display = 'none';
        dropzone.style.display = 'block';
        btnSubmit.disabled = true;
        progressPanel.style.display = 'none';
        if (pollInterval) {
            clearInterval(pollInterval);
            pollInterval = null;
        }
    }

    // 點擊事件
    dropzone.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', (e) => handleFile(e.target.files[0]));
    btnRemoveFile.addEventListener('click', resetFile);

    // 拖曳事件
    dropzone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropzone.classList.add('dragover');
    });

    dropzone.addEventListener('dragleave', () => {
        dropzone.classList.remove('dragover');
    });

    dropzone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropzone.classList.remove('dragover');
        if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
            handleFile(e.dataTransfer.files[0]);
        }
    });

    // 提交上傳
    btnSubmit.addEventListener('click', function() {
        if (!selectedFile) return;

        btnSubmit.disabled = true;
        btnRemoveFile.disabled = true;
        progressPanel.style.display = 'block';
        progressBar.style.width = '0%';
        progressBar.style.background = 'linear-gradient(90deg, var(--primary), var(--secondary))';
        percentText.textContent = '0%';
        statusTitle.textContent = '正在上傳檔案...';
        
        addLog('開始上傳檔案至伺服器...', 'info');

        const formData = new FormData();
        formData.append('audio_file', selectedFile);

        // 使用 XMLHttpRequest 上傳以取得進度
        const xhr = new XMLHttpRequest();
        xhr.open('POST', '/upload', true);

        xhr.upload.addEventListener('progress', function(e) {
            if (e.lengthComputable) {
                const percent = Math.round((e.loaded / e.total) * 100);
                progressBar.style.width = percent + '%';
                percentText.textContent = percent + '%';
                if (percent === 100) {
                    statusTitle.textContent = '檔案上傳完成，等待伺服器回應...';
                    addLog('檔案上傳完畢，伺服器準備進行轉寫處理...', 'success');
                }
            }
        });

        xhr.onload = function() {
            if (xhr.status === 200) {
                const response = JSON.parse(xhr.responseText);
                const transcriptionId = response.transcription_id;
                addLog(`建立轉寫任務成功，任務 ID: ${transcriptionId}`, 'success');
                
                if (response.status === 'completed') {
                    addLog('轉寫完成！正在跳轉頁面...', 'success');
                    window.location.href = `/transcriptions/${transcriptionId}`;
                } else {
                    startPolling(transcriptionId);
                }
            } else {
                let errorMsg = '上傳失敗';
                try {
                    errorMsg = JSON.parse(xhr.responseText).error || errorMsg;
                } catch(e) {}
                handleError(errorMsg);
            }
        };

        xhr.onerror = function() {
            handleError('網路連線錯誤，上傳失敗。');
        };

        xhr.send(formData);
    });

    function handleError(message) {
        addLog(`[錯誤] ${message}`, 'error');
        statusTitle.textContent = '轉寫失敗';
        percentText.textContent = '❌';
        progressBar.style.background = 'var(--primary)';
        progressBar.style.width = '100%';
        btnSubmit.disabled = false;
        btnRemoveFile.disabled = false;
    }

    // 輪詢狀態
    function startPolling(id) {
        statusTitle.textContent = '語音轉寫中，請稍候...';
        addLog('開始向伺服器輪詢轉寫狀態...', 'info');
        
        let dots = '';
        pollInterval = setInterval(function() {
            // 跑馬燈 loading 效果
            dots = dots.length >= 3 ? '' : dots + '.';
            statusTitle.textContent = '語音轉寫中，請稍候' + dots;

            fetch(`/transcriptions/${id}/status`)
                .then(res => res.json())
                .then(data => {
                    if (data.status === 'completed') {
                        clearInterval(pollInterval);
                        addLog('語音辨識完成！段落對齊成功！正在跳轉...', 'success');
                        setTimeout(() => {
                            window.location.href = `/transcriptions/${id}`;
                        }, 1000);
                    } else if (data.status === 'failed') {
                        clearInterval(pollInterval);
                        handleError(data.error || '語音辨識失敗');
                    } else {
                        addLog('語音處理中...（這可能需要幾十秒，取決於音訊長度）');
                    }
                })
                .catch(err => {
                    addLog('輪詢狀態時發生網路異常，重試中...');
                });
        }, 3000);
    }
});
