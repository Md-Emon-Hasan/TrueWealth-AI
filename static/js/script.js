$(document).ready(function() {
    let sessionId = generateSessionId();
    let isFirstMessage = true;
    
    // Theme toggle functionality
    $('#themeToggleBtn').click(function() {
        const currentTheme = $('html').attr('data-bs-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        $('html').attr('data-bs-theme', newTheme);
        
        // Update icon
        $(this).html(`<i class="fas fa-${newTheme === 'dark' ? 'sun' : 'moon'}"></i>`);
        
        // Save preference
        localStorage.setItem('theme', newTheme);
    });
    
    // Check for saved theme preference
    const savedTheme = localStorage.getItem('theme') || 'light';
    $('html').attr('data-bs-theme', savedTheme);
    $('#themeToggleBtn').html(`<i class="fas fa-${savedTheme === 'dark' ? 'sun' : 'moon'}"></i>`);
    
    // Quick question click handler
    $('.quick-question').click(function() {
        const question = $(this).data('question');
        $('#userInput').val(question).focus();
    });
    
    // Send message handler
    $('#sendBtn').click(sendMessage);
    $('#userInput').keypress(function(e) {
        if (e.which === 13) {
            sendMessage();
        }
    });
    
    // New chat handler
    $('#newChatBtn').click(function() {
        sessionId = generateSessionId();
        isFirstMessage = true;
        $('#chatMessages').html('').hide();
        $('#welcomeMessage').fadeIn();
    });
    
    function sendMessage() {
        const message = $('#userInput').val().trim();
        if (!message) return;
        
        // Add user message
        addMessage(message, 'user');
        $('#userInput').val('');
        
        // Hide welcome message after first message
        if (isFirstMessage) {
            $('#welcomeMessage').hide();
            $('#chatMessages').show();
            isFirstMessage = false;
        }
        
        // Show analyzing indicator
        $('#analyzingIndicator').fadeIn();
        
        // Scroll to bottom immediately after adding user message
        scrollToBottom();
        
        // Send to server
        $.ajax({
            url: '/chat',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                message: message,
                session_id: sessionId
            }),
            success: function(response) {
                addMessage(response.response, 'ai');
                scrollToBottom();
            },
            error: function() {
                addMessage("Sorry, I encountered an error. Please try again.", 'ai');
                scrollToBottom();
            }
        });
    }
    
    function addMessage(text, sender) {
        const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        const messageClass = sender === 'user' ? 'user-message' : 'ai-message';
        
        const messageHtml = `
            <div class="message ${messageClass} animate__animated animate__fadeIn">
                ${text}
                <span class="message-time">${time}</span>
            </div>
        `;
        
        $('#chatMessages').append(messageHtml);
    }
    
    function scrollToBottom() {
        const messagesContainer = $('.messages-container');
        messagesContainer.stop().animate({
            scrollTop: messagesContainer[0].scrollHeight
        }, 300);
    }
    
    function generateSessionId() {
        return 'session-' + Math.random().toString(36).substr(2, 9);
    }
});