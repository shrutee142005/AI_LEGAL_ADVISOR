const token =
    localStorage.getItem("access_token");


// ==================================================
// AUTH CHECK
// ==================================================

if (!token) {

    window.location.href = "/";

}


// ==================================================
// GET DOCUMENT ID FROM URL
// ==================================================

const urlParams =
    new URLSearchParams(
        window.location.search
    );


const documentId =
    urlParams.get(
        "document_id"
    );


// ==================================================
// DASHBOARD
// ==================================================

function goDashboard() {

    window.location.href =
        "/dashboard";

}


// ==================================================
// LOGOUT
// ==================================================

function logout() {

    localStorage.removeItem(
        "access_token"
    );

    window.location.href =
        "/";

}


// ==================================================
// LOAD CONVERSATIONS
// ==================================================

async function loadConversations() {

    const list =
        document.getElementById(
            "conversationList"
        );

    const count =
        document.getElementById(
            "conversationCount"
        );


    try {

        const response =
            await fetch(
                "/api/chat/conversations",
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

            list.innerHTML = `
                <div class="no-conversations">
                    Unable to load conversations.
                </div>
            `;

            return [];

        }


        const conversations =
            data.conversations || [];


        count.textContent =
            conversations.length;


        if (
            conversations.length === 0
        ) {

            list.innerHTML = `
                <div class="no-conversations">
                    No conversations yet.
                </div>
            `;

            return [];

        }


        list.innerHTML = "";


        conversations.forEach(
            conversation => {

                const item =
                    document.createElement(
                        "div"
                    );


                item.classList.add(
                    "conversation-item"
                );


                item.dataset.id =
                    conversation.id;


                item.innerHTML = `

                    <div class="conversation-main">

                        <div class="conversation-title">
                            ${escapeHtml(
                                conversation.title ||
                                "Legal Conversation"
                            )}
                        </div>

                        <div class="conversation-id">
                            Legal conversation
                        </div>

                    </div>

                    <button
                        class="delete-conversation-btn"
                        title="Delete conversation"
                        onclick="deleteConversation(event, ${conversation.id})"
                    >
                        🗑
                    </button>

                `;


                item.onclick =
                    function (event) {

                        /*
                         * If Delete button was clicked,
                         * do not select the conversation.
                         */

                        if (
                            event.target.closest(
                                ".delete-conversation-btn"
                            )
                        ) {

                            return;

                        }


                        selectConversation(
                            conversation.id
                        );

                    };


                list.appendChild(
                    item
                );

            }
        );


        return conversations;


    } catch (error) {

        console.error(
            "Conversation loading error:",
            error
        );


        list.innerHTML = `
            <div class="no-conversations">
                Server connection failed.
            </div>
        `;


        return [];

    }

}


// ==================================================
// CREATE CONVERSATION
// ==================================================

async function createConversation(
    silent = false
) {

    const status =
        document.getElementById(
            "statusMessage"
        );

    const button =
        document.querySelector(
            ".new-chat-btn"
        );


    if (!silent) {

        status.textContent =
            "Creating new conversation...";

    }


    if (button) {

        button.disabled = true;

    }


    try {

        console.log(
            "Creating conversation..."
        );


        const response =
            await fetch(
                "/api/chat/conversations",
                {

                    method: "POST",

                    headers: {

                        "Authorization":
                            "Bearer " + token,

                        "Content-Type":
                            "application/json"

                    },

                    body: JSON.stringify({

                        title:
                            "New Conversation"

                    })

                }
            );


        const data =
            await response.json();


        console.log(
            "Create conversation response:",
            response.status,
            data
        );


        if (!response.ok) {

            status.textContent =
                data.error ||
                "Unable to create conversation.";

            return null;

        }


        if (
            !data.conversation ||
            !data.conversation.id
        ) {

            status.textContent =
                "Conversation was not created correctly.";

            console.error(
                "Invalid conversation response:",
                data
            );

            return null;

        }


        const conversationId =
            data.conversation.id;


        console.log(
            "Conversation created:",
            conversationId
        );


        document.getElementById(
            "conversationId"
        ).value =
            conversationId;


        document.getElementById(
            "chatTitle"
        ).textContent =
            data.conversation.title ||
            "Legal Assistant";


        /*
         * If this conversation belongs to a
         * specific document, remember it.
         */

        if (documentId) {

            localStorage.setItem(

                `document_chat_${documentId}`,

                String(conversationId)

            );

        }


        await loadConversations();


        await selectConversation(
            conversationId
        );


        if (!silent) {

            status.textContent =
                "New conversation ready.";

        }


        /*
         * IMPORTANT:
         * Return the ID so askQuestion()
         * can continue using it.
         */

        return conversationId;


    } catch (error) {

        console.error(
            "Create conversation error:",
            error
        );


        status.textContent =
            "Server connection failed.";


        return null;


    } finally {

        if (button) {

            button.disabled =
                false;

        }

    }

}


// ==================================================
// AUTO CREATE / RESTORE DOCUMENT CONVERSATION
// ==================================================

async function initializeDocumentConversation() {

    if (!documentId) {

        return;

    }


    // ------------------------------------------------
    // Check stored conversation
    // ------------------------------------------------

    const storedConversationId =
        localStorage.getItem(
            `document_chat_${documentId}`
        );


    if (storedConversationId) {

        const conversations =
            await loadConversations();


        const exists =
            conversations.some(
                conversation =>
                    String(conversation.id) ===
                    String(storedConversationId)
            );


        if (exists) {

            await selectConversation(
                storedConversationId
            );

            return;

        }


        /*
         * Conversation was deleted.
         * Remove old localStorage reference.
         */

        localStorage.removeItem(
            `document_chat_${documentId}`
        );

    }


    // ------------------------------------------------
    // Automatically create conversation
    // ------------------------------------------------

    await createConversation(
        true
    );

}


// ==================================================
// SELECT CONVERSATION
// ==================================================

async function selectConversation(
    conversationId
) {

    document.getElementById(
        "conversationId"
    ).value =
        conversationId;


    const items =
        document.querySelectorAll(
            ".conversation-item"
        );


    items.forEach(
        item => {

            item.classList.remove(
                "active"
            );


            if (
                String(item.dataset.id) ===
                String(conversationId)
            ) {

                item.classList.add(
                    "active"
                );

            }

        }
    );


    await loadMessages();

}


// ==================================================
// DELETE CONVERSATION
// ==================================================

async function deleteConversation(
    event,
    conversationId
) {

    /*
     * Prevent the conversation itself from
     * being selected when delete is clicked.
     */

    if (event) {

        event.stopPropagation();

    }


    const confirmed =
        confirm(
            "Are you sure you want to delete this conversation?\n\nAll messages in this conversation will also be deleted."
        );


    if (!confirmed) {

        return;

    }


    const status =
        document.getElementById(
            "statusMessage"
        );


    const currentConversationId =
        document.getElementById(
            "conversationId"
        ).value;


    try {

        status.textContent =
            "Deleting conversation...";


        const response =
            await fetch(

                `/api/chat/conversations/${conversationId}`,

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

            status.textContent =
                data.error ||
                "Unable to delete conversation.";

            return;

        }


        /*
         * If this conversation was connected
         * with the current document, remove
         * its localStorage reference.
         */

        if (documentId) {

            const storedConversationId =
                localStorage.getItem(
                    `document_chat_${documentId}`
                );


            if (
                String(storedConversationId) ===
                String(conversationId)
            ) {

                localStorage.removeItem(
                    `document_chat_${documentId}`
                );

            }

        }


        /*
         * If deleted conversation was active,
         * clear the chat.
         */

        if (
            String(currentConversationId) ===
            String(conversationId)
        ) {

            document.getElementById(
                "conversationId"
            ).value = "";


            document.getElementById(
                "chatTitle"
            ).textContent =
                "Legal Assistant";


            showWelcomeScreen();

        }


        await loadConversations();


        /*
         * When a document chat is open and its
         * conversation was deleted, create a
         * fresh conversation automatically.
         *
         * This keeps the existing Ask AI flow
         * working.
         */

        if (
            documentId &&
            String(currentConversationId) ===
            String(conversationId)
        ) {

            await createConversation(
                true
            );

        }


        status.textContent =
            "Conversation deleted successfully.";


    } catch (error) {

        console.error(
            "Delete conversation error:",
            error
        );


        status.textContent =
            "Unable to connect to the server.";

    }

}


// ==================================================
// LOAD MESSAGES
// ==================================================

async function loadMessages() {

    const conversationId =
        document.getElementById(
            "conversationId"
        ).value;


    if (!conversationId) {

        return;

    }


    const messagesContainer =
        document.getElementById(
            "messages"
        );


    messagesContainer.innerHTML = `
        <div class="no-conversations">
            Loading conversation...
        </div>
    `;


    try {

        const response =
            await fetch(

                `/api/chat/conversations/${conversationId}/messages`,

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

            messagesContainer.innerHTML = `
                <div class="no-conversations">
                    Unable to load this conversation.
                </div>
            `;

            return;

        }


        messagesContainer.innerHTML = "";


        const messages =
            data.messages || [];


        if (
            messages.length === 0
        ) {

            showWelcomeScreen();

            return;

        }


        messages.forEach(
            message => {

                addMessage(
                    message.role,
                    message.content
                );

            }
        );


        scrollMessages();


    } catch (error) {

        console.error(
            "Load messages error:",
            error
        );


        messagesContainer.innerHTML = `
            <div class="no-conversations">
                Server connection failed.
            </div>
        `;

    }

}


// ==================================================
// ASK QUESTION
// ==================================================

async function askQuestion() {

    const questionInput =
        document.getElementById(
            "question"
        );


    let conversationId =
        document.getElementById(
            "conversationId"
        ).value;


    const askButton =
        document.getElementById(
            "askButton"
        );


    const status =
        document.getElementById(
            "statusMessage"
        );


    const question =
        questionInput.value.trim();


    // ------------------------------------------------
    // Question validation
    // ------------------------------------------------

    if (!question) {

        status.textContent =
            "Please enter a legal question.";

        questionInput.focus();

        return;

    }


    // ------------------------------------------------
    // Document validation
    // ------------------------------------------------

    if (!documentId) {

        status.textContent =
            "Please open this chat from a document.";

        return;

    }


    // ------------------------------------------------
    // Create conversation if needed
    // ------------------------------------------------

    let activeConversationId =
        conversationId;


    if (!activeConversationId) {

        activeConversationId =
            await createConversation(
                true
            );


        if (!activeConversationId) {

            return;

        }

    }


    // ------------------------------------------------
    // Add user message
    // ------------------------------------------------

    addMessage(
        "user",
        question
    );


    questionInput.value = "";

    autoResizeTextarea();


    askButton.disabled =
        true;


    status.textContent =
        "AI Legal Advisor is thinking...";


    showTypingIndicator();


    try {

        const response =
            await fetch(
                "/api/chat/ask",
                {

                    method: "POST",

                    headers: {

                        "Authorization":
                            "Bearer " + token,

                        "Content-Type":
                            "application/json"

                    },

                    body: JSON.stringify({

                        conversation_id:
                            parseInt(
                                activeConversationId
                            ),

                        document_id:
                            parseInt(
                                documentId
                            ),

                        question:
                            question

                    })

                }
            );


        const data =
            await response.json();


        removeTypingIndicator();


        if (!response.ok) {

            showError(
                data.error ||
                "Unable to get answer."
            );

            return;

        }


        addMessage(
            "assistant",
            data.answer
        );


        status.textContent =
            "Answer generated successfully.";


        await loadConversations();


        // Keep active conversation

        const items =
            document.querySelectorAll(
                ".conversation-item"
            );


        items.forEach(
            item => {

                if (
                    String(item.dataset.id) ===
                    String(activeConversationId)
                ) {

                    item.classList.add(
                        "active"
                    );

                }

            }
        );


    } catch (error) {

        console.error(
            "Ask question error:",
            error
        );


        removeTypingIndicator();


        showError(
            "Unable to connect to the server."
        );


    } finally {

        askButton.disabled =
            false;

    }

}


// ==================================================
// ADD MESSAGE
// ==================================================

function addMessage(
    role,
    content
) {

    const messages =
        document.getElementById(
            "messages"
        );


    const welcome =
        messages.querySelector(
            ".welcome-screen"
        );


    if (welcome) {

        welcome.remove();

    }


    const message =
        document.createElement(
            "div"
        );


    message.classList.add(
        "message"
    );


    if (
        role === "user"
    ) {

        message.classList.add(
            "user-message"
        );

    } else {

        message.classList.add(
            "ai-message"
        );

    }


    const roleText =
        role === "user"
            ? "You"
            : "AI Legal Advisor";


    message.innerHTML = `

        <div class="message-role">
            ${roleText}
        </div>

        <div>
            ${escapeHtml(content)}
        </div>

    `;


    messages.appendChild(
        message
    );


    scrollMessages();

}


// ==================================================
// WELCOME SCREEN
// ==================================================

function showWelcomeScreen() {

    const messages =
        document.getElementById(
            "messages"
        );


    messages.innerHTML = `

        <div class="welcome-screen">

            <div class="welcome-icon">
                ⚖
            </div>

            <h2>
                ${
                    documentId
                        ? "Ask about your document"
                        : "Welcome to your Legal Assistant"
                }
            </h2>

            <p>
                ${
                    documentId
                        ? "Ask questions about the selected legal document."
                        : "Create a conversation and ask a legal question."
                }
            </p>

            <div class="suggestions">

                <button
                    onclick="useSuggestion(
                        'What are the key points of this document?'
                    )"
                >
                    What are the key points of this document?
                </button>

                <button
                    onclick="useSuggestion(
                        'Can you explain the main points in simple words?'
                    )"
                >
                    Explain the main points simply
                </button>

            </div>

        </div>

    `;

}


// ==================================================
// SUGGESTION
// ==================================================

function useSuggestion(
    text
) {

    const input =
        document.getElementById(
            "question"
        );


    input.value =
        text;


    autoResizeTextarea();

    input.focus();

}


// ==================================================
// ENTER TO SEND
// ==================================================

function handleEnter(event) {

    if (
        event.key === "Enter" &&
        !event.shiftKey
    ) {

        event.preventDefault();

        askQuestion();

    }

}


// ==================================================
// TEXTAREA RESIZE
// ==================================================

function autoResizeTextarea() {

    const textarea =
        document.getElementById(
            "question"
        );


    textarea.style.height =
        "auto";


    textarea.style.height =
        Math.min(
            textarea.scrollHeight,
            130
        ) + "px";

}


// ==================================================
// TYPING INDICATOR
// ==================================================

function showTypingIndicator() {

    const messages =
        document.getElementById(
            "messages"
        );


    removeTypingIndicator();


    const typing =
        document.createElement(
            "div"
        );


    typing.id =
        "typingIndicator";


    typing.classList.add(
        "message",
        "ai-message"
    );


    typing.innerHTML = `

        <div class="message-role">
            AI Legal Advisor
        </div>

        <div class="typing-indicator">

            <span></span>
            <span></span>
            <span></span>

        </div>

    `;


    messages.appendChild(
        typing
    );


    scrollMessages();

}


// ==================================================
// REMOVE TYPING
// ==================================================

function removeTypingIndicator() {

    const typing =
        document.getElementById(
            "typingIndicator"
        );


    if (typing) {

        typing.remove();

    }

}


// ==================================================
// ERROR
// ==================================================

function showError(
    message
) {

    const status =
        document.getElementById(
            "statusMessage"
        );


    status.textContent =
        message;

}


// ==================================================
// SCROLL
// ==================================================

function scrollMessages() {

    const messages =
        document.getElementById(
            "messages"
        );


    setTimeout(
        () => {

            messages.scrollTop =
                messages.scrollHeight;

        },
        50
    );

}


// ==================================================
// ESCAPE HTML
// ==================================================

function escapeHtml(
    text
) {

    const div =
        document.createElement(
            "div"
        );


    div.textContent =
        text;


    return div.innerHTML;

}


// ==================================================
// INITIALIZE
// ==================================================

document.addEventListener(
    "DOMContentLoaded",
    async () => {

        const textarea =
            document.getElementById(
                "question"
            );


        if (textarea) {

            textarea.addEventListener(
                "input",
                autoResizeTextarea
            );

        }


        if (documentId) {

            await initializeDocumentConversation();

        } else {

            await loadConversations();

        }

    }
);