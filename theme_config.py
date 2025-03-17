"""
Theme configuration for the Deep Research Assistant.
Edit this file to customize the appearance of the application.
"""

# Default theme configuration (dark theme with green accents)
DEFAULT_THEME = {
    "colors": {
        # Primary colors
        "primary": "#00E5A0",
        "primary_hover": "#00C88A",
        "primary_light": "#3DFFB6",
        
        # Background colors
        "background": "#0A0C0F",
        "background_secondary": "#141820",
        
        # Surface colors
        "surface": "#141820",
        "surface_hover": "#202830",
        
        # Text colors
        "text": "#F2F2F2",
        "text_secondary": "#B0B0B8",
        
        # Border colors
        "border": "#202830",
        "border_accent": "#E54C00",
        
        # Status colors
        "success": "#00E5A0",
        "warning": "#E54C00",
        "error": "#F24236",
        "info": "#00E5A0",
    },
    "gradients": {
        # Text gradients
        "gradient_text": "linear-gradient(90deg, #00E5A0, #E54C00, #00E5A0)",
        "gradient_line": "linear-gradient(90deg, #141820, #00E5A0, #E54C00, #00E5A0, #141820)",
        
        # Background gradients
        "background_gradient": "linear-gradient(135deg, #0A0C0F, #141820)",
        "surface_gradient": "linear-gradient(135deg, #141820, #202830)",
        
        # Accent gradients
        "accent_gradient": "linear-gradient(to bottom, #00E5A0, #E54C00)",
    },
    "shadows": {
        "container": "0 8px 16px -2px rgba(7, 15, 24, 0.4), 0 4px 8px -1px rgba(7, 15, 24, 0.3)",
        "button": "0 4px 6px -1px rgba(0, 0, 0, 0.3), 0 2px 4px -1px rgba(0, 0, 0, 0.2)",
        "input_area": "0 -4px 12px rgba(0, 0, 0, 0.5)",
        "glow": "0 0 15px rgba(0, 229, 160, 0.3), 0 0 20px rgba(229, 76, 0, 0.2)",
    },
    "animations": {
        "glow_animation": "0 0 5px rgba(0, 229, 160, 0.3)",
        "glow_animation_mid": "0 0 15px rgba(0, 229, 160, 0.5)",
    },
    "typography": {
        "font_family": "'Geist Mono', monospace",
        "font_size_base": "1.1rem",
        "font_size_sm": "0.95rem",
        "font_size_lg": "1.25rem",
        "font_size_xl": "1.4rem",
    },
    "layout": {
        "border_radius": "0.75rem",
        "input_height": "120px",
        "container_padding": "1.25rem",
        "container_margin": "1.25rem",
    },
    "buttons": {
        "sidebar_new_chat": {
            "background": "#141820",
            "hover_background": "#202830",
            "text_color": "#F2F2F2",
            "border_color": "#202830",
        },
        "sidebar_chat": {
            "background": "transparent",
            "hover_background": "#202830",
            "active_background": "#202830",
            "text_color": "#F2F2F2",
            "border_color": "transparent",
        },
        "primary": {
            "background": "#00E5A0",
            "hover_background": "#00C88A",
            "text_color": "#0A0C0F",
            "border_color": "transparent",
        },
        "secondary": {
            "background": "#141820",
            "hover_background": "#202830",
            "text_color": "#F2F2F2",
            "border_color": "#202830",
        },
    },
}

# Blue theme configuration
BLUE_THEME = {
    "colors": {
        # Primary colors
        "primary": "#3B82F6",
        "primary_hover": "#2563EB",
        "primary_light": "#60A5FA",
        
        # Background colors
        "background": "#0F172A",
        "background_secondary": "#1E293B",
        
        # Surface colors
        "surface": "#1E293B",
        "surface_hover": "#334155",
        
        # Text colors
        "text": "#F1F5F9",
        "text_secondary": "#CBD5E1",
        
        # Border colors
        "border": "#334155",
        "border_accent": "#F59E0B",
        
        # Status colors
        "success": "#10B981",
        "warning": "#F59E0B",
        "error": "#EF4444",
        "info": "#3B82F6",
    },
    "gradients": {
        # Text gradients - Updated to use the blue theme colors
        "gradient_text": "linear-gradient(90deg, #3B82F6, #F59E0B, #3B82F6)",
        "gradient_line": "linear-gradient(90deg, #1E293B, #3B82F6, #F59E0B, #3B82F6, #1E293B)",
        
        # Background gradients
        "background_gradient": "linear-gradient(135deg, #0F172A, #1E293B)",
        "surface_gradient": "linear-gradient(135deg, #1E293B, #334155)",
        
        # Accent gradients
        "accent_gradient": "linear-gradient(to bottom, #3B82F6, #F59E0B)",
    },
    "shadows": {
        "container": "0 8px 16px -2px rgba(7, 15, 24, 0.4), 0 4px 8px -1px rgba(7, 15, 24, 0.3)",
        "button": "0 4px 6px -1px rgba(0, 0, 0, 0.3), 0 2px 4px -1px rgba(0, 0, 0, 0.2)",
        "input_area": "0 -4px 12px rgba(0, 0, 0, 0.5)",
        "glow": "0 0 15px rgba(59, 130, 246, 0.3), 0 0 20px rgba(245, 158, 11, 0.2)",
    },
    "animations": {
        "glow_animation": "0 0 5px rgba(59, 130, 246, 0.3)",
        "glow_animation_mid": "0 0 15px rgba(59, 130, 246, 0.5)",
    },
    "typography": {
        "font_family": "'Geist Mono', monospace",
        "font_size_base": "1.1rem",
        "font_size_sm": "0.95rem",
        "font_size_lg": "1.25rem",
        "font_size_xl": "1.4rem",
    },
    "layout": {
        "border_radius": "0.75rem",
        "input_height": "120px",
        "container_padding": "1.25rem",
        "container_margin": "1.25rem",
    },
    "buttons": {
        "sidebar_new_chat": {
            "background": "#1E293B",
            "hover_background": "#334155",
            "text_color": "#F1F5F9",
            "border_color": "#334155",
        },
        "sidebar_chat": {
            "background": "transparent",
            "hover_background": "#334155",
            "active_background": "#334155",
            "text_color": "#F1F5F9",
            "border_color": "transparent",
        },
        "primary": {
            "background": "#3B82F6",
            "hover_background": "#2563EB",
            "text_color": "#F1F5F9",
            "border_color": "transparent",
        },
        "secondary": {
            "background": "#1E293B",
            "hover_background": "#334155",
            "text_color": "#F1F5F9",
            "border_color": "#334155",
        },
    },
}

# Purple theme configuration
PURPLE_THEME = {
    "colors": {
        # Primary colors
        "primary": "#8B5CF6",
        "primary_hover": "#7C3AED",
        "primary_light": "#A78BFA",
        
        # Background colors
        "background": "#0F0720",
        "background_secondary": "#1E1033",
        
        # Surface colors
        "surface": "#1E1033",
        "surface_hover": "#33204D",
        
        # Text colors
        "text": "#F5F3FF",
        "text_secondary": "#DDD6FE",
        
        # Border colors
        "border": "#33204D",
        "border_accent": "#EC4899",
        
        # Status colors
        "success": "#10B981",
        "warning": "#F59E0B",
        "error": "#EF4444",
        "info": "#8B5CF6",
    },
    "gradients": {
        # Text gradients - Updated to use the purple theme colors
        "gradient_text": "linear-gradient(90deg, #8B5CF6, #EC4899, #8B5CF6)",
        "gradient_line": "linear-gradient(90deg, #1E1033, #8B5CF6, #EC4899, #8B5CF6, #1E1033)",
        
        # Background gradients
        "background_gradient": "linear-gradient(135deg, #0F0720, #1E1033)",
        "surface_gradient": "linear-gradient(135deg, #1E1033, #33204D)",
        
        # Accent gradients
        "accent_gradient": "linear-gradient(to bottom, #8B5CF6, #EC4899)",
    },
    "shadows": {
        "container": "0 8px 16px -2px rgba(7, 15, 24, 0.4), 0 4px 8px -1px rgba(7, 15, 24, 0.3)",
        "button": "0 4px 6px -1px rgba(0, 0, 0, 0.3), 0 2px 4px -1px rgba(0, 0, 0, 0.2)",
        "input_area": "0 -4px 12px rgba(0, 0, 0, 0.5)",
        "glow": "0 0 15px rgba(139, 92, 246, 0.3), 0 0 20px rgba(236, 72, 153, 0.2)",
    },
    "animations": {
        "glow_animation": "0 0 5px rgba(139, 92, 246, 0.3)",
        "glow_animation_mid": "0 0 15px rgba(139, 92, 246, 0.5)",
    },
    "typography": {
        "font_family": "'Geist Mono', monospace",
        "font_size_base": "1.1rem",
        "font_size_sm": "0.95rem",
        "font_size_lg": "1.25rem",
        "font_size_xl": "1.4rem",
    },
    "layout": {
        "border_radius": "0.75rem",
        "input_height": "120px",
        "container_padding": "1.25rem",
        "container_margin": "1.25rem",
    },
    "buttons": {
        "sidebar_new_chat": {
            "background": "#1E1033",
            "hover_background": "#33204D",
            "text_color": "#F5F3FF",
            "border_color": "#33204D",
        },
        "sidebar_chat": {
            "background": "transparent",
            "hover_background": "#33204D",
            "active_background": "#33204D",
            "text_color": "#F5F3FF",
            "border_color": "transparent",
        },
        "primary": {
            "background": "#8B5CF6",
            "hover_background": "#7C3AED",
            "text_color": "#F5F3FF",
            "border_color": "transparent",
        },
        "secondary": {
            "background": "#1E1033",
            "hover_background": "#33204D",
            "text_color": "#F5F3FF",
            "border_color": "#33204D",
        },
    },
}

# Happy Hues Palette #4 theme configuration
HAPPY_HUES_THEME = {
    "colors": {
        # Primary colors - Using the purple from Happy Hues
        "primary": "#7f5af0",
        "primary_hover": "#6a48d7",
        "primary_light": "#9e80f5",
        
        # Background colors - Using the dark backgrounds from Happy Hues
        "background": "#16161a",
        "background_secondary": "#242629",
        
        # Surface colors
        "surface": "#242629",
        "surface_hover": "#2e3035",
        
        # Text colors
        "text": "#fffffe",
        "text_secondary": "#94a1b2",
        
        # Border colors
        "border": "#2e3035",
        "border_accent": "#2cb67d",
        
        # Status colors
        "success": "#2cb67d",
        "warning": "#ffd803",
        "error": "#ef4565",
        "info": "#7f5af0",
        
        # Icon colors - Adding specific colors for the chatbot icons
        "icon_primary": "#7f5af0",    # Purple for primary icon
        "icon_secondary": "#ffd803",  # Yellow for secondary icon
        
        # Message bar background
        "message_bar_bg": "#242629",  # Using the secondary background color
    },
    "gradients": {
        # Text gradients - Using Happy Hues colors
        "gradient_text": "linear-gradient(90deg, #7f5af0, #2cb67d, #7f5af0)",
        "gradient_line": "linear-gradient(90deg, #242629, #7f5af0, #2cb67d, #7f5af0, #242629)",
        
        # Background gradients
        "background_gradient": "linear-gradient(135deg, #16161a, #242629)",
        "surface_gradient": "linear-gradient(135deg, #242629, #2e3035)",
        
        # Accent gradients
        "accent_gradient": "linear-gradient(to bottom, #7f5af0, #2cb67d)",
    },
    "shadows": {
        "container": "0 8px 16px -2px rgba(7, 15, 24, 0.4), 0 4px 8px -1px rgba(7, 15, 24, 0.3)",
        "button": "0 4px 6px -1px rgba(0, 0, 0, 0.3), 0 2px 4px -1px rgba(0, 0, 0, 0.2)",
        "input_area": "0 -4px 12px rgba(0, 0, 0, 0.5)",
        "glow": "0 0 15px rgba(127, 90, 240, 0.3), 0 0 20px rgba(44, 182, 125, 0.2)",
    },
    "animations": {
        "glow_animation": "0 0 5px rgba(127, 90, 240, 0.3)",
        "glow_animation_mid": "0 0 15px rgba(127, 90, 240, 0.5)",
    },
    "typography": {
        "font_family": "'Geist Mono', monospace",
        "font_size_base": "1.1rem",
        "font_size_sm": "0.95rem",
        "font_size_lg": "1.25rem",
        "font_size_xl": "1.4rem",
    },
    "layout": {
        "border_radius": "0.75rem",
        "input_height": "120px",
        "container_padding": "1.25rem",
        "container_margin": "1.25rem",
    },
    "buttons": {
        "sidebar_new_chat": {
            "background": "#242629",
            "hover_background": "#2e3035",
            "text_color": "#fffffe",
            "border_color": "#2e3035",
        },
        "sidebar_chat": {
            "background": "transparent",
            "hover_background": "#2e3035",
            "active_background": "#2e3035",
            "text_color": "#fffffe",
            "border_color": "transparent",
        },
        "primary": {
            "background": "#7f5af0",
            "hover_background": "#6a48d7",
            "text_color": "#fffffe",
            "border_color": "transparent",
        },
        "secondary": {
            "background": "#242629",
            "hover_background": "#2e3035",
            "text_color": "#fffffe",
            "border_color": "#2e3035",
        },
    },
}

# Function to get the active theme
def get_active_theme():
    """Get the currently active theme configuration"""
    # Change this line to use a different theme
    # Options: DEFAULT_THEME, BLUE_THEME, PURPLE_THEME, HAPPY_HUES_THEME
    return HAPPY_HUES_THEME  # Using the Happy Hues palette #4 theme 