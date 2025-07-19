// Camera functionality for profile picture and cover image uploads
class CameraUpload {
    constructor() {
        this.video = null;
        this.canvas = null;
        this.stream = null;
        this.currentInput = null;
        this.currentPreview = null;
        this.currentBadge = null;
        this.modal = null;
        this.init();
    }

    init() {
        this.createModal();
        this.bindEvents();
    }

    createModal() {
        const modalHTML = `
            <div id="camera-modal" class="camera-modal" style="display: none;">
                <div class="camera-modal-content">
                    <div class="camera-modal-header">
                        <h3>Camera Capture</h3>
                        <button class="camera-close-btn" onclick="cameraUpload.closeModal()">
                            <i class="fa fa-times"></i>
                        </button>
                    </div>
                    <div class="camera-modal-body">
                        <video id="camera-video" autoplay playsinline></video>
                        <canvas id="camera-canvas" style="display: none;"></canvas>
                        <div class="camera-controls">
                            <button class="camera-btn camera-capture-btn" onclick="cameraUpload.capture()">
                                <i class="fa fa-camera"></i> Capture
                            </button>
                            <button class="camera-btn camera-switch-btn" onclick="cameraUpload.switchCamera()">
                                <i class="fa fa-sync"></i> Switch Camera
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        document.body.insertAdjacentHTML('beforeend', modalHTML);
        this.modal = document.getElementById('camera-modal');
        this.video = document.getElementById('camera-video');
        this.canvas = document.getElementById('camera-canvas');
    }

    bindEvents() {
        // Profile picture camera button
        const profileCameraBtn = document.querySelector('.profile-upload-btn');
        if (profileCameraBtn) {
            profileCameraBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.openCamera('id_profile_pic', '.profile-pic-preview img', '.profile-pic-preview .file-badge');
            });
        }

        // Cover image camera button
        const coverCameraBtn = document.querySelector('.cover-upload-btn');
        if (coverCameraBtn) {
            coverCameraBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.openCamera('id_cover_image', '.cover-upload-row .cover-img-preview', '.cover-upload-row .file-badge');
            });
        }
    }

    async openCamera(inputId, previewSelector, badgeSelector) {
        this.currentInput = document.getElementById(inputId);
        this.currentPreview = document.querySelector(previewSelector);
        this.currentBadge = document.querySelector(badgeSelector);

        try {
            this.stream = await navigator.mediaDevices.getUserMedia({ 
                video: { 
                    facingMode: 'user',
                    width: { ideal: 1280 },
                    height: { ideal: 720 }
                } 
            });
            this.video.srcObject = this.stream;
            this.modal.style.display = 'flex';
        } catch (err) {
            console.error('Error accessing camera:', err);
            alert('Unable to access camera. Please try again.');
        }
    }

    async capture() {
        if (!this.video.srcObject) return;

        const context = this.canvas.getContext('2d');
        
        // Let CSS handle the dimensions - capture at a reasonable size
        this.canvas.width = 400;
        this.canvas.height = 400;

        // Calculate aspect ratio and crop to fit the target dimensions
        const videoAspect = this.video.videoWidth / this.video.videoHeight;
        const canvasAspect = this.canvas.width / this.canvas.height;
        
        let sourceX = 0;
        let sourceY = 0;
        let sourceWidth = this.video.videoWidth;
        let sourceHeight = this.video.videoHeight;

        if (videoAspect > canvasAspect) {
            // Video is wider than target - crop width
            sourceWidth = this.video.videoHeight * canvasAspect;
            sourceX = (this.video.videoWidth - sourceWidth) / 2;
        } else {
            // Video is taller than target - crop height
            sourceHeight = this.video.videoWidth / canvasAspect;
            sourceY = (this.video.videoHeight - sourceHeight) / 2;
        }

        // Draw the cropped and resized image
        context.drawImage(
            this.video, 
            sourceX, sourceY, sourceWidth, sourceHeight,
            0, 0, this.canvas.width, this.canvas.height
        );

        this.canvas.toBlob((blob) => {
            const file = new File([blob], 'camera-capture.jpg', { type: 'image/jpeg' });
            this.setFile(file);
            this.closeModal();
        }, 'image/jpeg', 0.9);
    }

    setFile(file) {
        if (this.currentInput) {
            const dataTransfer = new DataTransfer();
            dataTransfer.items.add(file);
            this.currentInput.files = dataTransfer.files;
            
            // Update preview
            if (this.currentPreview) {
                const url = URL.createObjectURL(file);
                this.currentPreview.src = url;
                this.currentPreview.style.display = 'block';
            }

            // Update badge
            if (this.currentBadge) {
                this.currentBadge.textContent = file.name;
            }

            // Trigger change event
            this.currentInput.dispatchEvent(new Event('change', { bubbles: true }));
        }
    }

    async switchCamera() {
        if (this.stream) {
            this.stream.getTracks().forEach(track => track.stop());
        }

        try {
            const devices = await navigator.mediaDevices.enumerateDevices();
            const videoDevices = devices.filter(device => device.kind === 'videoinput');
            
            if (videoDevices.length > 1) {
                const currentFacingMode = this.video.srcObject ? 
                    this.video.srcObject.getVideoTracks()[0].getSettings().facingMode : 'user';
                
                const newFacingMode = currentFacingMode === 'user' ? 'environment' : 'user';
                
                this.stream = await navigator.mediaDevices.getUserMedia({
                    video: { 
                        facingMode: newFacingMode,
                        width: { ideal: 1280 },
                        height: { ideal: 720 }
                    }
                });
                this.video.srcObject = this.stream;
            }
        } catch (err) {
            console.error('Error switching camera:', err);
        }
    }

    closeModal() {
        if (this.stream) {
            this.stream.getTracks().forEach(track => track.stop());
        }
        this.modal.style.display = 'none';
        this.currentInput = null;
        this.currentPreview = null;
        this.currentBadge = null;
    }
}

// Initialize camera functionality when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.cameraUpload = new CameraUpload();
}); 