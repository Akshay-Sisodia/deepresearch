"""
Theme configuration for the Deep Research Assistant application.
This file centralizes all styling variables and configurations.
"""

# Import the active theme from theme_config
from theme_config import get_active_theme

# Get the active theme
ACTIVE_THEME = get_active_theme()

# Color palette
COLORS = ACTIVE_THEME["colors"]

# Gradients
GRADIENTS = ACTIVE_THEME["gradients"]

# Typography
TYPOGRAPHY = ACTIVE_THEME["typography"]

# Layout
LAYOUT = ACTIVE_THEME["layout"]

# Shadows
SHADOWS = ACTIVE_THEME["shadows"]

# Animations
ANIMATIONS = ACTIVE_THEME["animations"]

# Transitions
TRANSITIONS = {
    "default": "all 0.2s ease",
}

# Button styles
BUTTONS = {
    "primary": {
        "background": COLORS["primary"],
        "color": COLORS["background"],
        "hover_background": COLORS["primary_hover"],
        "font_weight": "600",
    },
    "sidebar_new_chat": {
        "background": ACTIVE_THEME["buttons"]["sidebar_new_chat"]["background"],
        "color": ACTIVE_THEME["buttons"]["sidebar_new_chat"]["text_color"],
        "hover_background": ACTIVE_THEME["buttons"]["sidebar_new_chat"]["hover_background"],
        "font_weight": "600",
    },
    "sidebar_chat_history": {
        "background": ACTIVE_THEME["buttons"]["sidebar_chat"]["background"],
        "color": ACTIVE_THEME["buttons"]["sidebar_chat"]["text_color"],
        "hover_background": ACTIVE_THEME["buttons"]["sidebar_chat"]["hover_background"],
        "border": COLORS["border"],
        "hover_border": COLORS["primary"],
    },
}

# Message container styles
MESSAGES = {
    "user": {
        "background": GRADIENTS["surface_gradient"],
        "border": f"1px solid {COLORS['border']}",
        "shadow": SHADOWS["container"],
    },
    "assistant": {
        "background": GRADIENTS["surface_gradient"],
        "border": f"1px solid {COLORS['border']}",
        "shadow": SHADOWS["container"],
    },
}

# Credibility indicators
CREDIBILITY = {
    "high": {
        "background": COLORS["success"],
        "border": COLORS["success"],
    },
    "medium": {
        "background": COLORS["warning"],
        "border": COLORS["warning"],
    },
    "low": {
        "background": COLORS["error"],
        "border": COLORS["error"],
    },
}

def customize_theme(theme_config=None):
    """
    Customize the theme with the provided configuration.
    
    Args:
        theme_config (dict): A dictionary containing theme configuration overrides.
            Example: {
                "colors": {
                    "primary": "#FF5733",
                    "background": "#000000"
                },
                "typography": {
                    "font_family": "'Roboto Mono', monospace"
                }
            }
    """
    if not theme_config:
        return
    
    # Update colors
    if "colors" in theme_config:
        for key, value in theme_config["colors"].items():
            if key in COLORS:
                COLORS[key] = value
    
    # Update gradients
    if "gradients" in theme_config:
        for key, value in theme_config["gradients"].items():
            if key in GRADIENTS:
                GRADIENTS[key] = value
    
    # Update typography
    if "typography" in theme_config:
        for key, value in theme_config["typography"].items():
            if key in TYPOGRAPHY:
                TYPOGRAPHY[key] = value
    
    # Update layout
    if "layout" in theme_config:
        for key, value in theme_config["layout"].items():
            if key in LAYOUT:
                LAYOUT[key] = value
    
    # Update shadows
    if "shadows" in theme_config:
        for key, value in theme_config["shadows"].items():
            if key in SHADOWS:
                SHADOWS[key] = value
    
    # Update animations
    if "animations" in theme_config:
        for key, value in theme_config["animations"].items():
            if key in ANIMATIONS:
                ANIMATIONS[key] = value
    
    # Update transitions
    if "transitions" in theme_config:
        for key, value in theme_config["transitions"].items():
            if key in TRANSITIONS:
                TRANSITIONS[key] = value
    
    # Update buttons
    if "buttons" in theme_config:
        for button_type, button_config in theme_config["buttons"].items():
            if button_type in BUTTONS:
                for key, value in button_config.items():
                    if key in BUTTONS[button_type]:
                        BUTTONS[button_type][key] = value
    
    # Update messages
    if "messages" in theme_config:
        for message_type, message_config in theme_config["messages"].items():
            if message_type in MESSAGES:
                for key, value in message_config.items():
                    if key in MESSAGES[message_type]:
                        MESSAGES[message_type][key] = value
    
    # Update credibility indicators
    if "credibility" in theme_config:
        for indicator_type, indicator_config in theme_config["credibility"].items():
            if indicator_type in CREDIBILITY:
                for key, value in indicator_config.items():
                    if key in CREDIBILITY[indicator_type]:
                        CREDIBILITY[indicator_type][key] = value
    
    # Update gradients after colors have been updated
    GRADIENTS["background_gradient"] = theme_config.get("gradients", {}).get("background_gradient", f"linear-gradient(135deg, {COLORS['background']}, {COLORS['background_secondary']})")
    GRADIENTS["surface_gradient"] = theme_config.get("gradients", {}).get("surface_gradient", f"linear-gradient(135deg, {COLORS['surface']}, {COLORS['surface_hover']})")
    GRADIENTS["gradient_text"] = theme_config.get("gradients", {}).get("gradient_text", f"linear-gradient(90deg, {COLORS['primary']}, {COLORS['border_accent']}, {COLORS['primary']})")
    GRADIENTS["gradient_line"] = theme_config.get("gradients", {}).get("gradient_line", f"linear-gradient(90deg, {COLORS['surface']}, {COLORS['primary']}, {COLORS['border_accent']}, {COLORS['primary']}, {COLORS['surface']})")
    GRADIENTS["accent_gradient"] = theme_config.get("gradients", {}).get("accent_gradient", f"linear-gradient(to bottom, {COLORS['primary']}, {COLORS['border_accent']})")

def get_css_variables():
    """Generate CSS variables from theme configuration"""
    css_vars = [
        ":root {",
    ]
    
    # Add colors
    for name, value in COLORS.items():
        css_vars.append(f"    --{name.replace('_', '-')}: {value};")
    
    # Add gradients
    for name, value in GRADIENTS.items():
        css_vars.append(f"    --{name.replace('_', '-')}: {value};")
    
    # Add typography
    for name, value in TYPOGRAPHY.items():
        css_vars.append(f"    --{name.replace('_', '-')}: {value};")
    
    # Add layout
    for name, value in LAYOUT.items():
        css_vars.append(f"    --{name.replace('_', '-')}: {value};")
    
    # Add shadows
    for name, value in SHADOWS.items():
        css_vars.append(f"    --{name.replace('_', '-')}: {value};")
    
    # Add animations
    for name, value in ANIMATIONS.items():
        css_vars.append(f"    --{name.replace('_', '-')}: {value};")
    
    css_vars.append("}")
    
    return "\n".join(css_vars)

def get_full_css():
    """Generate the complete CSS for the application"""
    css_variables = get_css_variables()
    
    return f"""
/* Import Geist Mono font - moved to top for proper loading */
@import url('https://fonts.googleapis.com/css2?family=Geist+Mono:wght@400;500;600;700&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@300;400;500;700&display=swap');

/* CSS Variables */
{css_variables}

/* Apply Geist Mono font globally - !important flag to override Streamlit defaults */
body, html, * {{
    font-family: var(--font-family) !important;
}}

/* Set base font size */
body {{
    font-size: var(--font-size-base) !important;
}}

/* Force font on specific Streamlit elements */
.stApp, .stMarkdown, .stMarkdown p, .stMarkdown span, .stButton button, 
.stTextInput input, .stTextArea textarea, .stSelectbox, .stMultiselect,
[data-testid="stSidebar"], [data-testid="stHeader"], [data-testid="baseButton-secondary"],
.css-1offfwp, .css-10trblm, .css-16idsys p, .stAlert, .stAlert p {{
    font-family: var(--font-family) !important;
}}

/* Global background */
.stApp {{
    background-color: var(--background) !important;
}}

/* Sidebar styling */
[data-testid="stSidebar"] {{
    background: var(--background-gradient) !important;
    border-right: 1px solid var(--border) !important;
}}

/* Button styling */
.stButton button {{
    background-color: var(--primary) !important;
    color: var(--background) !important;
    border-radius: var(--border-radius) !important;
    font-weight: 600 !important;
    transition: all 0.2s ease !important;
    border: none !important;
}}

.stButton button:hover {{
    background-color: var(--primary-hover) !important;
    transform: translateY(-1px) !important;
    box-shadow: var(--button) !important;
}}

/* Input area styling */
.stTextInput input, .stTextArea textarea {{
    background-color: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--border-radius) !important;
    color: var(--text) !important;
}}

/* Selectbox styling */
.stSelectbox, .stMultiselect {{
    background-color: var(--surface) !important;
    border-radius: var(--border-radius) !important;
}}

/* Text styling */
h1, h2, h3, h4, h5, h6, p, li, a {{
    color: var(--text) !important;
}}

/* Link styling */
a {{
    color: var(--primary-light) !important;
    text-decoration: none !important;
}}

a:hover {{
    color: var(--primary) !important;
    text-decoration: underline !important;
}}

/* Animation classes */
@keyframes spin {{
    0% {{ transform: rotate(0deg); }}
    100% {{ transform: rotate(360deg); }}
}}

@keyframes pulse {{
    0% {{ transform: scale(0.8); opacity: 0.3; }}
    50% {{ transform: scale(1.2); opacity: 1; }}
    100% {{ transform: scale(0.8); opacity: 0.3; }}
}}

@keyframes wave {{
    0% {{ transform: translateY(0px); }}
    25% {{ transform: translateY(-3px); }}
    50% {{ transform: translateY(0px); }}
    75% {{ transform: translateY(3px); }}
    100% {{ transform: translateY(0px); }}
}}

@keyframes gradient-pulse {{
    0% {{ background-size: 100% auto; opacity: 0.7; }}
    50% {{ background-size: 200% auto; opacity: 1; }}
    100% {{ background-size: 100% auto; opacity: 0.7; }}
}}

@keyframes gradient-flow {{
    0% {{ background-position: 0% 50%; }}
    50% {{ background-position: 100% 50%; }}
    100% {{ background-position: 0% 50%; }}
}}

@keyframes line-pulse {{
    0% {{ height: 2px; opacity: 0.7; }}
    50% {{ height: 3px; opacity: 1; }}
    100% {{ height: 2px; opacity: 0.7; }}
}}

@keyframes fade-in {{
    0% {{ opacity: 0; transform: translateY(10px); }}
    100% {{ opacity: 1; transform: translateY(0); }}
}}

@keyframes slide-in {{
    0% {{ transform: translateX(-20px); opacity: 0; }}
    100% {{ transform: translateX(0); opacity: 1; }}
}}

@keyframes glow {{
    0% {{ box-shadow: var(--glow-animation); }}
    50% {{ box-shadow: var(--glow-animation-mid); }}
    100% {{ box-shadow: var(--glow-animation); }}
}}

.gradient-text {{
    background: var(--gradient-text);
    background-size: 200% auto;
    color: transparent;
    -webkit-background-clip: text;
    background-clip: text;
    display: inline-block;
    font-weight: 600;
    text-shadow: var(--glow);
    letter-spacing: 0.5px;
}}

.animated-gradient-text {{
    background: var(--gradient-text);
    background-size: 200% auto;
    color: transparent;
    -webkit-background-clip: text;
    background-clip: text;
    animation: gradient-flow 3s linear infinite;
    display: inline-block;
    font-weight: 600;
    text-shadow: var(--glow);
    letter-spacing: 0.5px;
}}

.pulsating-wave {{
    background: var(--gradient-text);
    background-size: 200% auto;
    color: transparent;
    -webkit-background-clip: text;
    background-clip: text;
    animation: gradient-flow 3s linear infinite, gradient-pulse 2s ease-in-out infinite;
    display: inline-block;
    font-weight: 600;
    text-shadow: var(--glow);
    letter-spacing: 0.5px;
    text-align: center;
    width: 100%;
    line-height: 1.5;
}}

.gradient-line {{
    width: 100%;
    height: 2px;
    background: var(--gradient-line);
    background-size: 200% auto;
    animation: gradient-flow 3s linear infinite, line-pulse 2s ease-in-out infinite;
    border-radius: 2px;
    box-shadow: var(--glow-animation);
}}

.fade-in {{
    animation: fade-in 0.5s ease-out forwards;
}}

.slide-in {{
    animation: slide-in 0.4s ease-out forwards;
}}

.glow-container {{
    animation: glow 3s infinite ease-in-out;
}}

.message-container {{
    animation: fade-in 0.5s ease-out forwards;
    position: relative;
    overflow: hidden;
}}

.research-header {{
    animation: slide-in 0.4s ease-out forwards;
    font-weight: 600;
    margin-bottom: 0.75rem;
    color: var(--primary);
    font-size: 1.15rem;
}}

/* Chat message styling */
.stChatMessage {{
    background: var(--surface-gradient) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--border-radius) !important;
    box-shadow: var(--container) !important;
}}

/* Divider styling */
hr {{
    border-color: var(--border) !important;
}}

/* Scrollbar styling */
::-webkit-scrollbar {{
    width: 8px;
    height: 8px;
}}

::-webkit-scrollbar-track {{
    background: var(--background-secondary);
}}

::-webkit-scrollbar-thumb {{
    background: var(--surface-hover);
    border-radius: 4px;
}}

::-webkit-scrollbar-thumb:hover {{
    background: var(--primary);
}}
""" 