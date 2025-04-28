// DOM Elements
const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');
const selectedFile = document.getElementById('selectedFile');
const fileName = document.getElementById('fileName');
const invoiceForm = document.getElementById('invoiceForm');
const resultsContainer = document.getElementById('resultsContainer');
const toastContainer = document.getElementById('toastContainer');
const voiceNotification = document.getElementById('voiceNotification');
const audioPlayer = document.getElementById('audioPlayer');
const processButton = document.getElementById('processButton');
const voiceMessage = document.getElementById('voiceMessage');

// State Management
let currentFile = null;
let isProcessing = false;

// Event Listeners
document.addEventListener('DOMContentLoaded', () => {
    // Show upload form by default (in production, this would be gated by auth)
    document.getElementById('uploadForm').classList.remove('hidden');
});

// Drag and Drop Handlers
['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
    dropZone.addEventListener(eventName, preventDefaults, false);
    document.body.addEventListener(eventName, preventDefaults, false);
});

['dragenter', 'dragover'].forEach(eventName => {
    dropZone.addEventListener(eventName, highlight, false);
});

['dragleave', 'drop'].forEach(eventName => {
    dropZone.addEventListener(eventName, unhighlight, false);
});

dropZone.addEventListener('drop', handleDrop, false);
fileInput.addEventListener('change', handleFileSelect);
dropZone.addEventListener('click', () => fileInput.click());

function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

function highlight(e) {
    dropZone.classList.add('drag-over');
}

function unhighlight(e) {
    dropZone.classList.remove('drag-over');
}

function handleDrop(e) {
    const dt = e.dataTransfer;
    const files = dt.files;
    handleFiles(files);
}

function handleFileSelect(e) {
    const files = e.target.files;
    handleFiles(files);
}

function handleFiles(files) {
    if (files.length > 0) {
        const file = files[0];
        if (file.type === 'application/pdf') {
            showSelectedFile(file);
            processButton.disabled = false;
        } else {
            showToast('Please upload a PDF file', 'error');
        }
    }
}

function showSelectedFile(file) {
    fileName.textContent = file.name;
    selectedFile.classList.remove('hidden');
    dropZone.classList.add('has-file');
}

// Form Submit Handler
invoiceForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    try {
        showToast('Processing invoice...', 'info');
        processButton.disabled = true;
        processButton.innerHTML = '<span class="spinner"></span> Processing...';

        const response = await fetch('/process-invoice', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error('Failed to process invoice');
        }

        const data = await response.json();
        displayResults(data);
        showToast('Invoice processed successfully!', 'success');
        
        // Twitter conversion tracking event
        twq('event', 'tw-pmaca-pmaca', {
            // You can add additional parameters here if needed
            value: data.extractedInfo?.totalAmount || 0,
            currency: data.extractedInfo?.currency || 'USD',
            status: 1  // Successful conversion
        });
        
        if (data.voiceSummary) {
            showVoiceNotification(data.voiceSummary);
        }
    } catch (error) {
        console.error('Error:', error);
        showToast('Error processing invoice', 'error');
    } finally {
        processButton.disabled = false;
        processButton.textContent = 'Process Invoice';
    }
});

// Display Results
function displayResults(data) {
    // Display PDF Information
    displayPDFInfo(data.pdfInfo);
    
    // Display Vendor Information
    displayVendorInfo(data.vendorInfo);
    
    // Display Extracted Information
    displayExtractedInfo(data.extractedInfo);
    
    // Display Line Items
    displayLineItems(data.lineItems);
    
    // Display Validation Results
    displayValidationResults(data.validationResults);
    
    // Show results container
    resultsContainer.classList.remove('hidden');
}

function displayPDFInfo(pdfInfo) {
    const documentInfo = document.getElementById('documentInfo');
    const technicalInfo = document.getElementById('technicalInfo');
    
    documentInfo.innerHTML = `
        <p><strong>Created:</strong> ${pdfInfo.creationDate}</p>
        <p><strong>Modified:</strong> ${pdfInfo.modificationDate}</p>
        <p><strong>Author:</strong> ${pdfInfo.author || 'N/A'}</p>
        <p><strong>Producer:</strong> ${pdfInfo.producer || 'N/A'}</p>
    `;
    
    technicalInfo.innerHTML = `
        <p><strong>Version:</strong> ${pdfInfo.version}</p>
        <p><strong>Pages:</strong> ${pdfInfo.pageCount}</p>
        <p><strong>File Size:</strong> ${formatFileSize(pdfInfo.fileSize)}</p>
        <p><strong>Encrypted:</strong> ${pdfInfo.encrypted ? 'Yes' : 'No'}</p>
    `;
}

function displayVendorInfo(vendorInfo) {
    const vendorDetails = document.getElementById('vendorDetails');
    const transactionHistory = document.getElementById('transactionHistory');
    
    vendorDetails.innerHTML = `
        <div class="vendor-details-grid">
            <p><strong>Name:</strong> ${vendorInfo.name}</p>
            <p><strong>Tax ID:</strong> ${vendorInfo.taxId}</p>
            <p><strong>Address:</strong> ${vendorInfo.address}</p>
            <p><strong>CRM ID:</strong> ${vendorInfo.crmId}</p>
        </div>
    `;
    
    if (vendorInfo.transactions && vendorInfo.transactions.length > 0) {
        const transactionsHtml = vendorInfo.transactions
            .map(t => `
                <div class="transaction-item">
                    <p><strong>Date:</strong> ${t.date}</p>
                    <p><strong>Amount:</strong> ${formatCurrency(t.amount)}</p>
                    <p><strong>Status:</strong> ${t.status}</p>
                </div>
            `).join('');
        transactionHistory.innerHTML = transactionsHtml;
    } else {
        transactionHistory.innerHTML = '<p>No transaction history available</p>';
    }
}

function displayExtractedInfo(extractedInfo) {
    const extractedInfoElement = document.getElementById('extractedInfo');
    extractedInfoElement.innerHTML = `
        <div class="extracted-info-grid">
            <p><strong>Invoice Number:</strong> ${extractedInfo.invoiceNumber}</p>
            <p><strong>Date:</strong> ${extractedInfo.date}</p>
            <p><strong>Due Date:</strong> ${extractedInfo.dueDate}</p>
            <p><strong>Total Amount:</strong> ${formatCurrency(extractedInfo.totalAmount)}</p>
            <p><strong>Tax Amount:</strong> ${formatCurrency(extractedInfo.taxAmount)}</p>
            <p><strong>Currency:</strong> ${extractedInfo.currency}</p>
        </div>
    `;
}

function displayLineItems(lineItems) {
    const lineItemsBody = document.getElementById('lineItems');
    lineItemsBody.innerHTML = lineItems.map(item => `
        <tr>
            <td>${item.description}</td>
            <td>${item.quantity}</td>
            <td>${formatCurrency(item.unitPrice)}</td>
            <td>${formatCurrency(item.amount)}</td>
        </tr>
    `).join('');
}

function displayValidationResults(validationResults) {
    const validationResultsElement = document.getElementById('validationResults');
    validationResultsElement.innerHTML = validationResults.map(result => `
        <div class="validation-item ${result.status.toLowerCase()}">
            <span class="validation-icon"></span>
            <span class="validation-message">${result.message}</span>
        </div>
    `).join('');
}

// UI Helpers
function showLoadingState() {
    const submitButton = invoiceForm.querySelector('button[type="submit"]');
    submitButton.disabled = true;
    submitButton.innerHTML = `
        <svg class="animate-spin h-5 w-5 mr-3" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        Processing...
    `;
}

function hideLoadingState() {
    const submitButton = invoiceForm.querySelector('button[type="submit"]');
    submitButton.disabled = false;
    submitButton.textContent = 'Process Invoice';
}

function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    
    toastContainer.appendChild(toast);
    
    // Auto remove after 3 seconds
    setTimeout(() => {
        toast.classList.add('fade-out');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

function showVoiceNotification(voiceSummaryUrl) {
    voiceMessage.textContent = 'Voice summary available';
    voiceNotification.classList.remove('hidden');
    
    voiceNotification.onclick = () => {
        const audio = new Audio(voiceSummaryUrl);
        audio.play();
    };
}

// Utility Functions
function formatCurrency(amount, currency = 'USD') {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: currency
    }).format(amount);
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Authentication State Management (simplified for demo)
function checkAuthState() {
    // In a real app, this would check session/token validity
    const isAuthenticated = true; // Hardcoded for demo
    
    if (isAuthenticated) {
        document.getElementById('uploadForm').classList.remove('hidden');
        document.getElementById('loginPrompt').classList.add('hidden');
    } else {
        document.getElementById('uploadForm').classList.add('hidden');
        document.getElementById('loginPrompt').classList.remove('hidden');
    }
}

// Initialize authentication state
checkAuthState(); 