const token = localStorage.getItem("access_token");


// ==================================================
// CHECK LOGIN
// ==================================================

if (!token) {

    window.location.href = "/";

}


// ==================================================
// LOGOUT
// ==================================================

function logout() {

    localStorage.removeItem("access_token");

    window.location.href = "/";

}


// ==================================================
// LOAD DOCUMENTS
// ==================================================

async function loadDocuments() {

    const documentsList =
        document.getElementById("documentsList");


    documentsList.innerHTML =
        `<div class="loading">
            Loading documents...
        </div>`;


    try {

        const response = await fetch(
            "/api/documents",
            {
                method: "GET",

                headers: {
                    "Authorization":
                        "Bearer " + token
                }
            }
        );


        const data =
            await response.json();


        if (!response.ok) {

            documentsList.innerHTML =
                `<div class="empty-state">
                    Unable to load documents.
                </div>`;

            return;
        }


        if (
            !data.documents ||
            data.documents.length === 0
        ) {

            documentsList.innerHTML =
                `<div class="empty-state">
                    No documents uploaded yet.
                </div>`;

            return;
        }


        documentsList.innerHTML =
            data.documents
                .map(document => createDocumentCard(document))
                .join("");


    } catch (error) {

        console.error(error);

        documentsList.innerHTML =
            `<div class="empty-state">
                Server connection failed.
            </div>`;
    }

}


// ==================================================
// CREATE DOCUMENT CARD
// ==================================================

function createDocumentCard(document) {

    const date =
        document.uploaded_at
            ? new Date(document.uploaded_at)
                .toLocaleString()
            : "Date unavailable";


    return `

        <div
            class="document-card"
            id="document-${document.id}"
        >

            <div class="document-top">

                <div class="document-info">

                    <div class="document-icon">
                        📄
                    </div>

                    <div>

                        <div class="document-name">
                            ${escapeHtml(document.filename)}
                        </div>

                        <div class="document-date">
                            ${date}
                        </div>

                    </div>

                </div>

            </div>


            <div class="document-actions">

                <button
                    class="action-btn analysis-btn"
                    onclick="toggleAnalysis(${document.id})"
                >
                    Analysis
                </button>


                <button
                    class="action-btn chat-btn"
                    onclick="openDocumentChat(${document.id})"
                >
                    Ask AI
                </button>


                <button
                    class="action-btn delete-btn"
                    onclick="deleteDocument(${document.id})"
                >
                    Delete
                </button>

            </div>


            <div
                id="analysis-${document.id}"
                class="analysis-box"
            >

                <div class="analysis-loading">
                    Loading analysis...
                </div>

            </div>

        </div>

    `;
}


// ==================================================
// TOGGLE ANALYSIS
// ==================================================

async function toggleAnalysis(documentId) {

    const box =
        document.getElementById(
            `analysis-${documentId}`
        );


    if (box.classList.contains("visible")) {

        box.classList.remove("visible");

        return;
    }


    box.classList.add("visible");


    box.innerHTML =
        `<div class="analysis-loading">
            Loading document analysis...
        </div>`;


    try {

        const response =
            await fetch(
                `/api/documents/${documentId}`,
                {
                    method: "GET",

                    headers: {
                        "Authorization":
                            "Bearer " + token
                    }
                }
            );


        const data =
            await response.json();


        if (!response.ok) {

            box.innerHTML =
                `<p class="analysis-loading">
                    ${escapeHtml(
                        data.error ||
                        "Unable to load analysis."
                    )}
                </p>`;

            return;
        }


        const document =
            data.document;


        /*
         * Different backend versions may return
         * analysis in different fields.
         */

        const analysis =
            document.analysis ||
            document.document_analysis ||
            document.ai_analysis ||
            null;


        if (!analysis) {

            box.innerHTML =
                `<div class="analysis-section">

                    <h4>
                        Document
                    </h4>

                    <p>
                        ${escapeHtml(
                            document.extracted_text ||
                            "Analysis is not available yet."
                        )}
                    </p>

                </div>`;

            return;
        }


        box.innerHTML =
            renderAnalysis(analysis);


    } catch (error) {

        console.error(error);

        box.innerHTML =
            `<p class="analysis-loading">
                Unable to connect to server.
            </p>`;
    }

}


// ==================================================
// RENDER ANALYSIS
// ==================================================

function renderAnalysis(analysis) {

    /*
     * If backend sends analysis as a plain string,
     * show it directly.
     */

    if (typeof analysis === "string") {

        return `

            <h3 class="analysis-title">
                AI Document Analysis
            </h3>

            <div class="analysis-section">

                <p>
                    ${escapeHtml(analysis)}
                </p>

            </div>

            <button
                class="action-btn chat-btn"
                onclick="openCurrentChatFromAnalysis(this)"
            >
                Ask AI about this document
            </button>

        `;
    }


    /*
     * If backend sends structured JSON,
     * render common fields.
     */

    let html = `

        <h3 class="analysis-title">
            AI Document Analysis
        </h3>

    `;


    if (analysis.summary) {

        html += `

            <div class="analysis-section">

                <h4>
                    Summary
                </h4>

                <p>
                    ${escapeHtml(
                        analysis.summary
                    )}
                </p>

            </div>

        `;
    }


    if (analysis.overview) {

        html += `

            <div class="analysis-section">

                <h4>
                    Overview
                </h4>

                <p>
                    ${escapeHtml(
                        analysis.overview
                    )}
                </p>

            </div>

        `;
    }


    if (
        analysis.key_points &&
        Array.isArray(analysis.key_points)
    ) {

        html += `

            <div class="analysis-section">

                <h4>
                    Key Points
                </h4>

                <ul>

                    ${
                        analysis.key_points
                            .map(
                                point =>
                                    `<li>
                                        ${escapeHtml(point)}
                                    </li>`
                            )
                            .join("")
                    }

                </ul>

            </div>

        `;
    }


    if (
        analysis.main_types &&
        Array.isArray(analysis.main_types)
    ) {

        html += `

            <div class="analysis-section">

                <h4>
                    Main Types
                </h4>

                <ul>

                    ${
                        analysis.main_types
                            .map(
                                item =>
                                    `<li>
                                        ${escapeHtml(item)}
                                    </li>`
                            )
                            .join("")
                    }

                </ul>

            </div>

        `;
    }


    if (
        analysis.importance &&
        Array.isArray(analysis.importance)
    ) {

        html += `

            <div class="analysis-section">

                <h4>
                    Importance
                </h4>

                <ul>

                    ${
                        analysis.importance
                            .map(
                                item =>
                                    `<li>
                                        ${escapeHtml(item)}
                                    </li>`
                            )
                            .join("")
                    }

                </ul>

            </div>

        `;
    }


    return html;

}


// ==================================================
// OPEN DOCUMENT CHAT
// ==================================================

function openDocumentChat(documentId) {

    /*
     * IMPORTANT:
     * Document ID is passed to chat.
     *
     * Later chat.js can read:
     *
     * new URLSearchParams(
     *     window.location.search
     * ).get("document_id")
     */

    window.location.href =
        `/chat?document_id=${documentId}`;

}


// ==================================================
// UPLOAD DOCUMENT
// ==================================================

async function uploadDocument() {

    const fileInput =
        document.getElementById("pdfFile");

    const message =
        document.getElementById("uploadMessage");

    const uploadBtn =
        document.getElementById("uploadBtn");


    if (!fileInput.files.length) {

        message.textContent =
            "Please select a PDF.";

        return;
    }


    const file =
        fileInput.files[0];


    if (
        !file.name
            .toLowerCase()
            .endsWith(".pdf")
    ) {

        message.textContent =
            "Only PDF files are allowed.";

        return;
    }


    const formData =
        new FormData();


    formData.append(
        "file",
        file
    );


    message.textContent =
        "Uploading and analyzing PDF...";


    uploadBtn.disabled = true;


    try {

        const response =
            await fetch(
                "/api/documents/upload",
                {
                    method: "POST",

                    headers: {
                        "Authorization":
                            "Bearer " + token
                    },

                    body: formData
                }
            );


        const data =
            await response.json();


        if (!response.ok) {

            message.textContent =
                data.error ||
                "Upload failed.";

            return;
        }


        message.textContent =
            "✓ PDF uploaded and analyzed successfully.";


        fileInput.value = "";


        await loadDocuments();


    } catch (error) {

        console.error(error);

        message.textContent =
            "Server connection failed.";

    } finally {

        uploadBtn.disabled = false;

    }

}


// ==================================================
// DELETE DOCUMENT
// ==================================================

async function deleteDocument(documentId) {

    const confirmed =
        confirm(
            "Are you sure you want to delete this document?"
        );


    if (!confirmed) {

        return;
    }


    try {

        const response =
            await fetch(
                `/api/documents/${documentId}`,
                {
                    method: "DELETE",

                    headers: {
                        "Authorization":
                            "Bearer " + token
                    }
                }
            );


        const data =
            await response.json();


        if (!response.ok) {

            alert(
                data.error ||
                "Failed to delete document."
            );

            return;
        }


        await loadDocuments();


    } catch (error) {

        console.error(error);

        alert(
            "Server connection failed."
        );

    }

}


// ==================================================
// ESCAPE HTML
// ==================================================

function escapeHtml(value) {

    if (value === null || value === undefined) {

        return "";
    }


    return String(value)

        .replaceAll("&", "&amp;")

        .replaceAll("<", "&lt;")

        .replaceAll(">", "&gt;")

        .replaceAll('"', "&quot;")

        .replaceAll("'", "&#039;");
}


// ==================================================
// INITIAL LOAD
// ==================================================

loadDocuments();