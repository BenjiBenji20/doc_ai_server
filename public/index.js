// ===================================
// Configuration
// ===================================
// 'https://doc-ai-server.vercel.app'
const CONFIG = {
    API_URL: 'http://localhost:8000',
    MAX_FILE_SIZE: 10 * 1024 * 1024, // 10MB
    ALLOWED_TYPES: ['image/jpeg', 'image/png', 'application/pdf'],
    ENDPOINTS: {
        PROCESS_AUTO: '/api/doc-ai/process-auto',
        VALIDATE_DATA: '/api/doc-ai/submit-validated-data',
        // add more here in the future if you have more processors
    }
};

// ===================================
// State Management
// ===================================
const state = {
    selectedFile: null,
    extractedData: null,
    processorUsed: null
};

// ===================================
// DOM Elements
// ===================================
const elements = {
    uploadArea: document.getElementById('uploadArea'),
    fileInput: document.getElementById('fileInput'),
    browseBtn: document.getElementById('browseBtn'),
    filePreview: document.getElementById('filePreview'),
    previewImage: document.getElementById('previewImage'),
    fileDetails: document.getElementById('fileDetails'),
    removeBtn: document.getElementById('removeBtn'),
    processBtn: document.getElementById('processBtn'),
    uploadSection: document.getElementById('uploadSection'),
    loadingSection: document.getElementById('loadingSection'),
    validationSection: document.getElementById('validationSection'),
    validationForm: document.getElementById('validationForm'),
    cancelBtn: document.getElementById('cancelBtn'),
    submitBtn: document.getElementById('submitBtn'),
    messageContainer: document.getElementById('messageContainer'),
    step2: document.getElementById('step2'),
    step3: document.getElementById('step3')
};

// ===================================
// Utility Functions
// ===================================
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

function isValidFileType(file) {
    return CONFIG.ALLOWED_TYPES.includes(file.type);
}

function isValidFileSize(file) {
    return file.size <= CONFIG.MAX_FILE_SIZE;
}

function showMessage(type, title, message) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;

    const icons = {
        success: '✓',
        error: '✕',
        warning: '⚠'
    };

    messageDiv.innerHTML = `
        <div class="message-icon">${icons[type]}</div>
        <div class="message-content">
            <h4>${title}</h4>
            <p>${message}</p>
        </div>
    `;

    elements.messageContainer.appendChild(messageDiv);

    // Auto-remove after 5 seconds
    setTimeout(() => {
        messageDiv.style.opacity = '0';
        setTimeout(() => messageDiv.remove(), 300);
    }, 5000);
}

function showSection(section) {
    elements.uploadSection.style.display = 'none';
    elements.loadingSection.style.display = 'none';
    elements.validationSection.style.display = 'none';

    if (section === 'upload') elements.uploadSection.style.display = 'block';
    if (section === 'loading') elements.loadingSection.style.display = 'block';
    if (section === 'validation') elements.validationSection.style.display = 'block';
}

// ===================================
// File Selection & Preview
// ===================================
function handleFileSelect(file) {
    // Validate file type
    if (!isValidFileType(file)) {
        showMessage('error', 'Invalid File Type',
            'Please upload a JPEG, PNG, or PDF file.');
        return;
    }

    // Validate file size
    if (!isValidFileSize(file)) {
        showMessage('error', 'File Too Large',
            `Maximum file size is ${formatFileSize(CONFIG.MAX_FILE_SIZE)}`);
        return;
    }

    // Store file
    state.selectedFile = file;

    // Show preview
    showFilePreview(file);
}

function showFilePreview(file) {
    elements.filePreview.style.display = 'block';

    // Show file details
    elements.fileDetails.innerHTML = `
        <strong>File name:</strong> ${file.name}<br>
        <strong>File size:</strong> ${formatFileSize(file.size)}<br>
        <strong>File type:</strong> ${file.type}
    `;

    // Show image preview for images
    if (file.type.startsWith('image/')) {
        const reader = new FileReader();
        reader.onload = (e) => {
            elements.previewImage.src = e.target.result;
            elements.previewImage.style.display = 'block';
        };
        reader.readAsDataURL(file);
    } else {
        elements.previewImage.style.display = 'none';
    }

    // Scroll to preview
    elements.filePreview.scrollIntoView({ behavior: 'smooth' });
}

function removeFile() {
    state.selectedFile = null;
    elements.filePreview.style.display = 'none';
    elements.fileInput.value = '';
    elements.previewImage.style.display = 'none';
}

// ===================================
// File Upload & Processing
// ===================================
async function processDocument() {
    if (!state.selectedFile) {
        showMessage('error', 'No File Selected', 'Please select a file to process.');
        return;
    }

    // Show loading state
    showSection('loading');
    const btnText = elements.processBtn.querySelector('.btn-text');
    const btnLoader = elements.processBtn.querySelector('.btn-loader');
    btnText.style.display = 'none';
    btnLoader.style.display = 'flex';
    elements.processBtn.disabled = true;

    // Simulate progress steps
    setTimeout(() => elements.step2.classList.add('active'), 1000);
    setTimeout(() => elements.step3.classList.add('active'), 2000);

    try {
        // Create FormData
        const formData = new FormData();
        formData.append('file', state.selectedFile);

        // Call API
        const response = await fetch(`${CONFIG.API_URL}${CONFIG.ENDPOINTS.PROCESS_AUTO}`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        // Store extracted data
        state.extractedData = data;
        state.processorUsed = data.processor_used;

        // Show validation form
        populateValidationForm(data);
        showSection('validation');

        showMessage('success', 'Extraction Complete',
            'Please review and verify the extracted information.');

    } catch (error) {
        console.error('Error processing document:', error);
        showMessage('error', 'Processing Failed',
            error.message || 'Failed to process document. Please try again.');
        showSection('upload');
    } finally {
        // Reset button state
        btnText.style.display = 'inline';
        btnLoader.style.display = 'none';
        elements.processBtn.disabled = false;
        // Reset progress steps
        elements.step2.classList.remove('active');
        elements.step3.classList.remove('active');
    }
}

// ===================================
// Validation Form Population
// ===================================
function populateValidationForm(data) {
    // Clear form first
    elements.validationForm.reset();

    // Show/hide sections based on what was detected
    const frontSection = document.getElementById('frontSection');
    const rearSection = document.getElementById('rearSection');

    if (data.processor_used === 'front') {
        frontSection.style.display = 'block';
        rearSection.style.display = 'none';
    } else if (data.processor_used === 'rear') {
        frontSection.style.display = 'none';
        rearSection.style.display = 'block';
    } else {
        frontSection.style.display = 'block';
        rearSection.style.display = 'block';
    }

    // Populate front data
    if (data.front_data) {
        setFieldValue('uniqueIdNumber', data.front_data.unique_id_number);
        setFieldValue('lastName', data.front_data.last_name);
        setFieldValue('firstName', data.front_data.first_name);
        setFieldValue('middleName', data.front_data.middle_name);
        setFieldValue('birthDate', data.front_data.birth_date);
        setFieldValue('completeAddress', data.front_data.complete_address);
    }

    // Populate rear data
    if (data.rear_data) {
        setFieldValue('issuedDate', data.rear_data.issued_date);
        setFieldValue('sex', data.rear_data.sex);
        setFieldValue('bloodType', data.rear_data.blood_type);
        setFieldValue('maritalStatus', data.rear_data.marital_status);
        setFieldValue('placeOfBirth', data.rear_data.place_of_birth);
    }
}

function setFieldValue(fieldId, value) {
    const field = document.getElementById(fieldId);
    if (field && value) {
        field.value = value;
        // Highlight fields that have data
        field.style.background = '#f0fdf4';
    }
}

// ===================================
// Form Submission
// ===================================
async function handleFormSubmit(e) {
    e.preventDefault();

    // Collect validated data
    const validatedData = {
        processor_used: state.processorUsed,
        front_data: null,
        rear_data: null
    };

    // Collect front data if visible
    if (document.getElementById('frontSection').style.display !== 'none') {
        validatedData.front_data = {
            unique_id_number: document.getElementById('uniqueIdNumber').value,
            last_name: document.getElementById('lastName').value,
            first_name: document.getElementById('firstName').value,
            middle_name: document.getElementById('middleName').value,
            birth_date: document.getElementById('birthDate').value,
            complete_address: document.getElementById('completeAddress').value
        };
    }

    // Collect rear data if visible
    if (document.getElementById('rearSection').style.display !== 'none') {
        validatedData.rear_data = {
            issued_date: document.getElementById('issuedDate').value,
            sex: document.getElementById('sex').value,
            blood_type: document.getElementById('bloodType').value,
            marital_status: document.getElementById('maritalStatus').value,
            place_of_birth: document.getElementById('placeOfBirth').value
        };
    }

    // Send validatedData to your backend endpoint
    const data = await fetch(`${CONFIG.API_URL}${CONFIG.ENDPOINTS.VALIDATE_DATA}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(validatedData)
    });

    const response = await data.json();

    // Show response message
    showMessage(
        response.success ? 'success' : 'failed', 
        response.description,
        response.message
    );

    // Reset and go back to upload
    setTimeout(() => {
        resetApp();
    }, 2000);
}

function cancelValidation() {
    if (confirm('Are you sure you want to cancel? All extracted data will be lost.')) {
        resetApp();
    }
}

function resetApp() {
    state.selectedFile = null;
    state.extractedData = null;
    state.processorUsed = null;
    removeFile();
    showSection('upload');
    elements.validationForm.reset();
}

// ===================================
// Event Listeners
// ===================================

// Browse button click
elements.browseBtn.addEventListener('click', () => {
    elements.fileInput.click();
});

// File input change
elements.fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        handleFileSelect(e.target.files[0]);
    }
});

// Upload area click
elements.uploadArea.addEventListener('click', () => {
    elements.fileInput.click();
});

// Drag and drop
elements.uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    elements.uploadArea.classList.add('drag-over');
});

elements.uploadArea.addEventListener('dragleave', () => {
    elements.uploadArea.classList.remove('drag-over');
});

elements.uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    elements.uploadArea.classList.remove('drag-over');

    if (e.dataTransfer.files.length > 0) {
        handleFileSelect(e.dataTransfer.files[0]);
    }
});

// Remove file button
elements.removeBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    removeFile();
});

// Process button
elements.processBtn.addEventListener('click', processDocument);

// Form submission
elements.validationForm.addEventListener('submit', handleFormSubmit);

// Cancel button
elements.cancelBtn.addEventListener('click', cancelValidation);

// ===================================
// Initialize
// ===================================
console.log('Document AI Client initialized');
console.log('API URL:', CONFIG.API_URL);
console.log('Ready to process documents!');