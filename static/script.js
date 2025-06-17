// Simple tips array
const tips = [
    "💡 Tip: Use contrasting colors for better visibility",
    "🎨 Tip: 45° rotation is most common for watermarks",
    "📏 Tip: Font size 36-50 works well for most images",
    "🔄 Tip: Adjust spacing to avoid overcrowding",
    "💾 Tip: PNG preserves transparency, JPG creates smaller files"
];

// Update tip every 7 seconds
let tipIndex = 0;
function updateTip() {
    document.getElementById('tipText').textContent = tips[tipIndex];
    tipIndex = (tipIndex + 1) % tips.length;
}
setInterval(updateTip, 7000);

// Font option functionality
function initializeFontOptions() {
    const defaultOption = document.getElementById('defaultFontOption');
    const uploadOption = document.getElementById('uploadFontOption');
    const defaultContainer = document.getElementById('defaultFontContainer');
    const uploadContainer = document.getElementById('uploadFontContainer');
    const defaultRadio = document.querySelector('input[value="default"]');
    const uploadRadio = document.querySelector('input[value="upload"]');

    function toggleFontOptions() {
        if (defaultRadio.checked) {
            defaultOption.classList.add('active');
            uploadOption.classList.remove('active');
            defaultContainer.classList.remove('disabled');
            uploadContainer.classList.add('disabled');
        } else {
            defaultOption.classList.remove('active');
            uploadOption.classList.add('active');
            defaultContainer.classList.add('disabled');
            uploadContainer.classList.remove('disabled');
        }
    }

    defaultRadio.addEventListener('change', toggleFontOptions);
    uploadRadio.addEventListener('change', toggleFontOptions);

    defaultOption.addEventListener('click', function (e) {
        if (e.target.type !== 'radio') {
            defaultRadio.checked = true;
            toggleFontOptions();
        }
    });

    uploadOption.addEventListener('click', function (e) {
        if (e.target.type !== 'radio') {
            uploadRadio.checked = true;
            toggleFontOptions();
        }
    });

    toggleFontOptions();
}

// File upload feedback
function initializeFileUpload() {
    const imageInput = document.getElementById('image');
    const fontInput = document.getElementById('fontUpload');

    function handleFileSelect(input) {
        input.addEventListener('change', function () {
            if (this.files && this.files[0]) {
                this.classList.add('file-selected');
            } else {
                this.classList.remove('file-selected');
            }
        });
    }

    handleFileSelect(imageInput);
    handleFileSelect(fontInput);
}

// Form handling
function initializeForm() {
    const form = document.querySelector('form');
    const generateBtn = document.getElementById('generateBtn');

    form.addEventListener('submit', function (e) {
        generateBtn.textContent = 'Generating...';
        generateBtn.disabled = true;

        setTimeout(() => {
            generateBtn.textContent = 'Generate Watermark';
            generateBtn.disabled = false;
        }, 2000);
    });

    // Prevent Enter key submission except on button
    document.querySelectorAll('input').forEach(input => {
        input.addEventListener('keydown', function (e) {
            if (e.key === 'Enter') {
                e.preventDefault();
            }
        });
    });
}

// Live preview functionality
document.querySelector('form').addEventListener('change', handleLivePreview);

async function handleLivePreview() {
    const form = document.querySelector('form');
    const formData = new FormData(form);

    const imageFile = formData.get("image");
    if (!imageFile) return;

    try {
        const response = await fetch('/preview', {
            method: 'POST',
            body: formData
        });

        if (response.ok) {
            const blob = await response.blob();
            const url = URL.createObjectURL(blob);

            // Show preview image and hide placeholder
            const previewImage = document.getElementById("previewImage");
            const placeholder = document.getElementById("previewPlaceholder");

            previewImage.src = url;
            previewImage.style.display = 'block';
            placeholder.style.display = 'none';
        } else {
            // Show placeholder if preview fails
            const previewImage = document.getElementById("previewImage");
            const placeholder = document.getElementById("previewPlaceholder");

            previewImage.style.display = 'none';
            placeholder.style.display = 'flex';
            placeholder.textContent = '⚠️ Preview failed - try again';
        }
    } catch (error) {
        console.error("Preview failed:", error);
        // Show placeholder on error
        const previewImage = document.getElementById("previewImage");
        const placeholder = document.getElementById("previewPlaceholder");

        previewImage.style.display = 'none';
        placeholder.style.display = 'flex';
        placeholder.textContent = '⚠️ Preview unavailable';
    }
}

// Initialize everything when DOM is ready
document.addEventListener('DOMContentLoaded', function () {
    initializeFontOptions();
    initializeFileUpload();
    initializeForm();
});