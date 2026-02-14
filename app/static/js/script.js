// Global state to store current boxes and image data
let currentBoxes = [];
let currentImageBase64 = null;

// --- DOM Elements ---
const fileInput = document.getElementById('file-input');
const editorSection = document.getElementById('editor-section');
const uploadSection = document.getElementById('upload-section');
const targetImage = document.getElementById('target-image');
const overlayLayer = document.getElementById('overlay-layer');
const loader = document.getElementById('loader');
const boxCountSpan = document.getElementById('box-count');

// --- Event Listeners ---

// Handle File Selection
fileInput.addEventListener('change', async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    // Show loader
    loader.style.display = 'flex';

    // Create FormData to send file
    const formData = new FormData();
    formData.append('file', file);

    try {
        // Send to backend
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) throw new Error('Upload failed');

        const data = await response.json();
        
        // Setup Editor
        setupEditor(data);

    } catch (error) {
        console.error(error);
        alert('Error processing image. Please try again.');
    } finally {
        loader.style.display = 'none';
    }
});

// --- Core Functions ---

function setupEditor(data) {
    // 1. Switch Views
    uploadSection.style.display = 'none';
    editorSection.style.display = 'flex';

    // 2. Load Image
    // The backend returns the image as a Base64 string
    currentImageBase64 = data.image_base64;
    targetImage.src = `data:image/jpeg;base64,${data.image_base64}`;

    // 3. Store Boxes
    // Add an 'active' property to track if it should be blurred
    currentBoxes = data.boxes.map(box => ({ ...box, active: true }));
    
    // 4. Draw Boxes Overlay
    // We need to wait for the image to load to ensure dimensions are correct,
    // though usually with base64 it's instant.
    targetImage.onload = () => {
        drawBoxes();
    };
}

function drawBoxes() {
    overlayLayer.innerHTML = ''; // Clear existing boxes
    let activeCount = 0;

    // Get the display size of the image vs its natural size
    // We need this scale factor because the image might be resized by CSS
    const scaleX = targetImage.clientWidth / targetImage.naturalWidth;
    const scaleY = targetImage.clientHeight / targetImage.naturalHeight;

    currentBoxes.forEach((box, index) => {
        if (box.active) activeCount++;

        const div = document.createElement('div');
        div.className = box.active ? 'blur-box' : 'blur-box inactive';
        
        // Scale coordinates to match the displayed image size
        div.style.left = `${box.x * scaleX}px`;
        div.style.top = `${box.y * scaleY}px`;
        div.style.width = `${box.w * scaleX}px`;
        div.style.height = `${box.h * scaleY}px`;

        // Add Click Handler
        div.onclick = () => toggleBox(index);

        // Tooltip
        div.title = box.active ? "Click to KEEP text (Don't Blur)" : "Click to BLUR text";

        overlayLayer.appendChild(div);
    });

    boxCountSpan.innerText = activeCount;
}

function toggleBox(index) {
    // Toggle the 'active' state
    currentBoxes[index].active = !currentBoxes[index].active;
    // Redraw to update colors
    drawBoxes();
}

async function processAndDownload() {
    if (!currentImageBase64) return;

    loader.style.display = 'flex';

    // Filter only the boxes that are still active (red)
    const boxesToBlur = currentBoxes.filter(b => b.active);

    const payload = {
        image_base64: currentImageBase64,
        boxes: boxesToBlur
    };

    try {
        const response = await fetch('/process', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        if (!response.ok) throw new Error('Processing failed');

        // Convert response to a Blob (binary large object)
        const blob = await response.blob();
        
        // Create a temporary link to trigger download
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = "privacy-protected-image.jpg";
        document.body.appendChild(a);
        a.click();
        
        // Cleanup
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);

    } catch (error) {
        console.error(error);
        alert('Failed to generate blurred image.');
    } finally {
        loader.style.display = 'none';
    }
}

function resetEditor() {
    currentBoxes = [];
    currentImageBase64 = null;
    targetImage.src = '';
    overlayLayer.innerHTML = '';
    fileInput.value = ''; // Reset file input
    
    editorSection.style.display = 'none';
    uploadSection.style.display = 'block';
}

// Handle window resize to adjust box positions
window.addEventListener('resize', drawBoxes);