class InvoiceExtractor {
    constructor() {
        this.apiBase = 'http://localhost:8000/api';
        this.invoices = [];
        this.currentInvoice = null;
        this.initializeEventListeners();
    }

    initializeEventListeners() {
        const uploadArea = document.getElementById('uploadArea');
        const fileInput = document.getElementById('fileInput');

        uploadArea.addEventListener('click', () => fileInput.click());

        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('border-blue-500', 'bg-blue-50', 'scale-105');
        });

        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('border-blue-500', 'bg-blue-50', 'scale-105');
        });

        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('border-blue-500', 'bg-blue-50', 'scale-105');
            if (e.dataTransfer.files.length > 0) {
                this.handleFileUpload(e.dataTransfer.files[0]);
            }
        });

        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                this.handleFileUpload(e.target.files[0]);
            }
        });
    }

    async handleFileUpload(file) {
        if (!file.type.includes('pdf')) {
            this.showError('Please upload a PDF file');
            return;
        }

        this.showUploadProgress(10, 'Uploading file...');

        try {
            // Upload file
            const formData = new FormData();
            formData.append('original_file', file);

            this.showUploadProgress(30, 'Creating invoice record...');
            const uploadResponse = await fetch(`${this.apiBase}/invoices/`, {
                method: 'POST',
                body: formData
            });

            if (!uploadResponse.ok) {
                throw new Error('Failed to upload file');
            }

            const invoice = await uploadResponse.json();
            this.invoices.unshift(invoice);
            this.showUploadProgress(60, 'Extracting information...');

            // Extract information
            const extractResponse = await fetch(
                `${this.apiBase}/invoices/${invoice.id}/extract_information/`,
                { method: 'POST' }
            );

            if (!extractResponse.ok) {
                throw new Error('Failed to extract information');
            }

            this.showUploadProgress(90, 'Processing results...');
            const extractionResult = await extractResponse.json();

            // Update invoice with extracted data
            const updatedInvoice = {
                ...invoice,
                ...extractionResult.extracted_data,
                extraction_method: extractionResult.extraction_method,
                confidence_score: extractionResult.confidence_score,
                raw_text: extractionResult.raw_text || ''
            };

            this.invoices[0] = updatedInvoice;
            this.currentInvoice = updatedInvoice;

            this.showUploadProgress(100, 'Complete!');
            setTimeout(() => {
                this.hideUploadProgress();
                this.updateInvoiceList();
                this.displayResults(updatedInvoice);
            }, 500);

        } catch (error) {
            this.hideUploadProgress();
            this.showError(`Error: ${error.message}`);
        }
    }

    showUploadProgress(percent, text) {
        const progressSection = document.getElementById('uploadProgress');
        const progressBar = document.getElementById('progressBar');
        const progressText = document.getElementById('progressText');

        progressSection.classList.remove('hidden');
        progressBar.style.width = `${percent}%`;
        progressText.textContent = text;
    }

    hideUploadProgress() {
        document.getElementById('uploadProgress').classList.add('hidden');
    }

    updateInvoiceList() {
        const invoiceList = document.getElementById('invoiceList');

        if (this.invoices.length === 0) {
            invoiceList.innerHTML = `
                <div class="text-center text-gray-500 py-8">
                    <i class="fas fa-file text-3xl opacity-50 mb-2"></i>
                    <p>No invoices uploaded yet</p>
                </div>
            `;
            return;
        }

        invoiceList.innerHTML = this.invoices.map(invoice => `
            <div class="invoice-item p-4 rounded-lg border-2 cursor-pointer transition-all ${
                this.currentInvoice?.id === invoice.id
                    ? 'border-blue-500 bg-blue-50 shadow-md'
                    : 'border-gray-200 hover:border-gray-300 hover:shadow-sm'
            }" onclick="app.selectInvoice(${invoice.id})">
                <div class="flex justify-between items-start mb-2">
                    <span class="font-medium text-gray-800">
                        ${invoice.invoice_number || 'Unknown Invoice'}
                    </span>
                    <span class="confidence-badge px-2 py-1 rounded-full text-xs border ${
                        this.getConfidenceColor(invoice.confidence_score)
                    }">
                        ${Math.round((invoice.confidence_score || 0) * 100)}%
                    </span>
                </div>
                <div class="text-sm text-gray-600 flex justify-between">
                    <span>${invoice.amount ? `$${invoice.amount}` : 'No amount'}</span>
                    <span class="text-xs opacity-75">${invoice.extraction_method || 'pending'}</span>
                </div>
            </div>
        `).join('');
    }

    selectInvoice(invoiceId) {
        this.currentInvoice = this.invoices.find(inv => inv.id === invoiceId);
        this.updateInvoiceList();
        this.displayResults(this.currentInvoice);
    }

    displayResults(invoice) {
        const resultsSection = document.getElementById('resultsSection');

        if (!invoice) {
            resultsSection.innerHTML = `
                <div class="text-center py-12">
                    <i class="fas fa-search text-5xl text-gray-300 mb-4"></i>
                    <h3 class="text-2xl font-semibold text-gray-600 mb-2">No Invoice Selected</h3>
                    <p class="text-gray-500">Upload an invoice or select one from the list to view details</p>
                </div>
            `;
            return;
        }

        resultsSection.innerHTML = `
            <div class="flex justify-between items-start mb-6">
                <h2 class="text-2xl font-semibold text-gray-800">Extraction Results</h2>
                <div class="flex space-x-2">
                    <span class="method-badge px-3 py-1 rounded-full text-sm border ${
                        this.getMethodColor(invoice.extraction_method)
                    }">
                        ${(invoice.extraction_method || 'unknown').replace(/_/g, ' ')}
                    </span>
                    <span class="confidence-badge px-3 py-1 rounded-full text-sm border ${
                        this.getConfidenceColor(invoice.confidence_score)
                    }">
                        ${Math.round((invoice.confidence_score || 0) * 100)}% confident
                    </span>
                </div>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
                <!-- Invoice Details -->
                <div class="space-y-4">
                    <h3 class="text-lg font-semibold text-gray-700 border-b pb-2">Invoice Details</h3>

                    ${this.createDetailItem('Invoice Number', invoice.invoice_number, 'hashtag')}
                    ${this.createDetailItem('Invoice Date', invoice.invoice_date, 'calendar')}
                    ${this.createDetailItem('Due Date', invoice.due_date, 'calendar-check')}
                    ${this.createDetailItem('Amount', invoice.amount ? `$${invoice.amount}` : null, 'dollar-sign', true)}
                </div>

                <!-- Extraction Info -->
                <div class="space-y-4">
                    <h3 class="text-lg font-semibold text-gray-700 border-b pb-2">Extraction Info</h3>

                    <div class="flex justify-between items-center py-2 border-b">
                        <span class="text-gray-600">Method:</span>
                        <span class="font-medium text-gray-800 capitalize">
                            ${(invoice.extraction_method || 'unknown').replace(/_/g, ' ')}
                        </span>
                    </div>

                    <div class="flex justify-between items-center py-2 border-b">
                        <span class="text-gray-600">Confidence:</span>
                        <div class="flex items-center space-x-2">
                            <div class="w-24 bg-gray-200 rounded-full h-2">
                                <div class="confidence-bar h-2 rounded-full transition-all duration-300 ${
                                    this.getConfidenceBarColor(invoice.confidence_score)
                                }" style="width: ${(invoice.confidence_score || 0) * 100}%"></div>
                            </div>
                            <span class="font-medium text-gray-800 w-12">
                                ${Math.round((invoice.confidence_score || 0) * 100)}%
                            </span>
                        </div>
                    </div>

                    <div class="flex justify-between items-center py-2 border-b">
                        <span class="text-gray-600">Uploaded:</span>
                        <span class="text-sm text-gray-600">
                            ${new Date(invoice.uploaded_at).toLocaleDateString()}
                        </span>
                    </div>
                </div>
            </div>

            <!-- Raw Text Preview -->
            <div>
                <h3 class="text-lg font-semibold text-gray-700 mb-3">Extracted Text</h3>
                <div class="bg-gray-50 rounded-lg p-4 max-h-60 overflow-y-auto">
                    <pre class="text-sm text-gray-600 whitespace-pre-wrap font-sans">${
                        invoice.raw_text || 'No text extracted'
                    }</pre>
                </div>
            </div>
        `;

        document.getElementById('errorMessage').classList.add('hidden');
    }

    createDetailItem(label, value, icon, isAmount = false) {
        return `
            <div class="flex justify-between items-center py-2 border-b">
                <div class="flex items-center space-x-3">
                    <i class="fas fa-${icon} text-gray-400"></i>
                    <span class="text-gray-600">${label}:</span>
                </div>
                <span class="font-medium ${isAmount ? 'text-green-600' : 'text-gray-800'}">
                    ${value || '<span class="text-gray-400 italic">Not found</span>'}
                </span>
            </div>
        `;
    }

    getConfidenceColor(score) {
        if (score >= 0.8) return 'text-green-600 bg-green-50 border-green-200';
        if (score >= 0.6) return 'text-yellow-600 bg-yellow-50 border-yellow-200';
        return 'text-red-600 bg-red-50 border-red-200';
    }

    getConfidenceBarColor(score) {
        if (score >= 0.8) return 'bg-green-500';
        if (score >= 0.6) return 'bg-yellow-500';
        return 'bg-red-500';
    }

    getMethodColor(method) {
        switch (method) {
            case 'demo_data': return 'text-purple-600 bg-purple-50 border-purple-200';
            case 'intelligent_patterns': return 'text-blue-600 bg-blue-50 border-blue-200';
            case 'filename_fallback': return 'text-orange-600 bg-orange-50 border-orange-200';
            default: return 'text-gray-600 bg-gray-50 border-gray-200';
        }
    }

    showError(message) {
        const errorSection = document.getElementById('errorMessage');
        const errorText = document.getElementById('errorText');

        errorText.textContent = message;
        errorSection.classList.remove('hidden');
    }
}

// Initialize the application
const app = new InvoiceExtractor();