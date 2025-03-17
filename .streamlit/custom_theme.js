// Function to apply Geist Mono font to all elements
function applyGeistMonoFont() {
  const allElements = document.querySelectorAll('*');
  allElements.forEach(el => {
    el.style.fontFamily = "'Geist Mono', monospace";
  });
}

// Apply font when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
  applyGeistMonoFont();
  
  // Set up a MutationObserver to apply font to new elements
  const fontObserver = new MutationObserver(function(mutations) {
    applyGeistMonoFont();
  });
  
  // Start observing the document body for changes
  fontObserver.observe(document.body, { 
    childList: true,
    subtree: true
  });
});

// Also run immediately in case the DOM is already loaded
applyGeistMonoFont();

// Custom JavaScript to apply styles after Streamlit components are loaded

// Function to apply styles to chat avatars
function styleAvatars() {
  // Find all avatar elements
  const userAvatars = document.querySelectorAll('[data-testid="stChatMessageAvatar"][data-avatar-for-user="true"]');
  const assistantAvatars = document.querySelectorAll('[data-testid="stChatMessageAvatar"]:not([data-avatar-for-user="true"])');
  
  // Style user avatars
  userAvatars.forEach(avatar => {
    avatar.style.backgroundColor = '#ffd803';
    avatar.style.border = 'none';
    avatar.style.boxShadow = 'none';
  });
  
  // Style assistant avatars
  assistantAvatars.forEach(avatar => {
    avatar.style.backgroundColor = '#7f5af0';
    avatar.style.border = 'none';
    avatar.style.boxShadow = 'none';
  });
  
  // Style SVGs inside avatars
  const avatarSvgs = document.querySelectorAll('[data-testid="stChatMessageAvatar"] svg');
  avatarSvgs.forEach(svg => {
    svg.style.fill = '#16161a';
  });
}

// Function to apply styles to chat containers
function styleChatContainers() {
  // Style chat message containers
  const chatMessages = document.querySelectorAll('.stChatMessage');
  chatMessages.forEach(message => {
    message.style.backgroundColor = '#242629';
    message.style.border = '1px solid #2e3035';
    message.style.borderRadius = '0.75rem';
    message.style.marginBottom = '1rem';
  });
  
  // Style chat input container
  const chatInputContainer = document.querySelector('.stChatInputContainer');
  if (chatInputContainer) {
    chatInputContainer.style.backgroundColor = '#242629';
    chatInputContainer.style.border = '1px solid #2e3035';
    chatInputContainer.style.borderRadius = '0.75rem';
    chatInputContainer.style.padding = '0.5rem';
  }
  
  // Style chat input
  const chatInput = document.querySelector('.stChatInputContainer textarea');
  if (chatInput) {
    chatInput.style.backgroundColor = '#242629';
    chatInput.style.color = '#fffffe';
    chatInput.style.border = 'none';
  }
  
  // Style chat input button
  const chatButton = document.querySelector('.stChatInputContainer button');
  if (chatButton) {
    chatButton.style.backgroundColor = '#7f5af0';
    chatButton.style.color = '#fffffe';
    chatButton.style.border = 'none';
    chatButton.style.borderRadius = '0.5rem';
    
    // Add hover effect
    chatButton.addEventListener('mouseenter', () => {
      chatButton.style.backgroundColor = '#6a48d7';
    });
    chatButton.addEventListener('mouseleave', () => {
      chatButton.style.backgroundColor = '#7f5af0';
    });
  }
}

// Apply theme styles when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
  // Apply initial styles
  styleAvatars();
  styleChatContainers();
  
  // Set up a MutationObserver to apply styles when new elements are added
  const themeObserver = new MutationObserver(function(mutations) {
    styleAvatars();
    styleChatContainers();
  });
  
  // Start observing the document body for changes
  themeObserver.observe(document.body, { 
    childList: true,
    subtree: true
  });
});

// Also run immediately in case the DOM is already loaded
styleAvatars();
styleChatContainers(); 