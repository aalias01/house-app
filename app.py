import streamlit as st

# Page configuration
st.set_page_config(
    page_title="House & Browse - Housing Affordability Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Add CSS and JavaScript for beautiful navigation bar styling
NAV_STYLES = """
<style>
    /* Main content container */
    .block-container {
        max-width: min(1440px, 100%) !important;
        padding-left: 3rem !important;
        padding-right: 3rem !important;
        padding-top: 1rem !important;
    }
    
    /* Reduce top spacing when header is hidden */
    .main .block-container {
        padding-top: 1rem !important;
    }
    
    /* Remove extra top margin */
    #MainMenu {
        visibility: hidden;
    }
    
    /* Adjust top spacing for content */
    section[data-testid="stMain"] {
        padding-top: 0 !important;
    }
    
    /* Navigation container - centered and aligned with content */
    .rc-overflow {
        max-width: min(1440px, 100%) !important;
        margin-left: auto !important;
        margin-right: auto !important;
        padding-left: 3rem !important;
        padding-right: 3rem !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        width: 100% !important;
        gap: 0.5rem !important;
    }
    
    /* Navigation links styling */
    [data-testid="stTopNavLink"] {
        padding: 0.5rem 1rem !important;
        border-radius: 8px !important;
        transition: all 0.3s ease !important;
        font-weight: 500 !important;
        margin: 0 0.25rem !important;
    }
    
    /* Hover effect for navigation links */
    [data-testid="stTopNavLink"]:hover {
        background-color: rgba(148, 163, 184, 0.1) !important;
        transform: translateY(-1px) !important;
    }
    
    /* Active/selected navigation link */
    [data-testid="stTopNavLink"][aria-current="page"],
    [data-testid="stTopNavLink"].nav-selected {
        background-color: rgba(59, 130, 246, 0.1) !important;
        color: rgb(59, 130, 246) !important;
        font-weight: 600 !important;
    }
    
    /* Hide all navigation links from navigation bar */
    [data-testid="stTopNavLink"][href*="map_explorer"],
    [data-testid="stTopNavLink"][href*="trend_comparison"],
    [data-testid="stTopNavLink"][href*="affordability_finder"],
    [data-testid="stTopNavLink"][href*="story"],
    [data-testid="stTopNavLink"][href*="intro"] {
        display: none !important;
        visibility: hidden !important;
        width: 0 !important;
        height: 0 !important;
        padding: 0 !important;
        margin: 0 !important;
        opacity: 0 !important;
    }
    
    /* Hide entire navigation bar completely */
    header[data-testid="stHeader"],
    nav[data-testid="stNavigation"],
    .rc-overflow,
    [data-testid="stTopNavLink"] {
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
        padding: 0 !important;
        margin: 0 !important;
        border: none !important;
        width: 0 !important;
        opacity: 0 !important;
    }
</style>
"""

NAV_SCRIPT = """
<script>
(function() {
    const NAV_SELECTOR = '.rc-overflow';
    const NAV_LINK_SELECTOR = '[data-testid="stTopNavLink"]';
    const STYLE_PROPS = {
        'max-width': 'min(1440px, 100%)',
        'margin-left': 'auto',
        'margin-right': 'auto',
        'padding-left': '3rem',
        'padding-right': '3rem'
    };
    
    function applyStyles(element) {
        Object.entries(STYLE_PROPS).forEach(([prop, value]) => {
            element.style.setProperty(prop, value, 'important');
        });
    }
    
    function hideDesignPages() {
        // Hide entire navigation header
        const header = document.querySelector('header[data-testid="stHeader"]');
        if (header) {
            header.style.setProperty('display', 'none', 'important');
            header.style.setProperty('visibility', 'hidden', 'important');
            header.style.setProperty('height', '0', 'important');
        }
        
        // Hide navigation container
        const navContainer = document.querySelector(NAV_SELECTOR);
        if (navContainer) {
            navContainer.style.setProperty('display', 'none', 'important');
            navContainer.style.setProperty('visibility', 'hidden', 'important');
        }
        
        // Hide all navigation links
        const allLinks = document.querySelectorAll(NAV_LINK_SELECTOR);
        allLinks.forEach(link => {
            link.style.setProperty('display', 'none', 'important');
            link.style.setProperty('visibility', 'hidden', 'important');
            link.style.setProperty('width', '0', 'important');
            link.style.setProperty('height', '0', 'important');
            link.style.setProperty('padding', '0', 'important');
            link.style.setProperty('margin', '0', 'important');
            link.style.setProperty('opacity', '0', 'important');
            link.style.setProperty('pointer-events', 'none', 'important');
        });
    }
    
    function alignNavigation() {
        const navContainer = document.querySelector(NAV_SELECTOR);
        if (!navContainer) return;
        
        const navLinks = navContainer.querySelectorAll(NAV_LINK_SELECTOR);
        if (navLinks.length === 0) return;
        
        // Apply container styles
        applyStyles(navContainer);
        navContainer.style.setProperty('display', 'flex', 'important');
        navContainer.style.setProperty('justify-content', 'center', 'important');
        navContainer.style.setProperty('align-items', 'center', 'important');
        navContainer.style.setProperty('width', '100%', 'important');
        navContainer.style.setProperty('gap', '0.5rem', 'important');
        
        // Style navigation links
        navLinks.forEach((link, index) => {
            const linkText = link.textContent || link.innerText || '';
            const linkHref = link.getAttribute('href') || '';
            const linkInnerHTML = link.innerHTML || '';
            
            // Skip if this is a design page, story page, or home page (should be handled by hideDesignPages)
            if (linkHref.includes('map_explorer') || linkHref.includes('trend_comparison') || linkHref.includes('affordability_finder') || 
                linkHref.includes('story') || linkText.includes('Story') ||
                linkHref.includes('intro') || linkText.includes('Home')) {
                return;
            }
            
            link.style.setProperty('padding', '0.5rem 1rem', 'important');
            link.style.setProperty('border-radius', '8px', 'important');
            link.style.setProperty('transition', 'all 0.3s ease', 'important');
            link.style.setProperty('font-weight', '500', 'important');
            link.style.setProperty('margin', '0 0.25rem', 'important');
            
        });
        
        // Style parent containers to match content alignment
        let parent = navContainer.parentElement;
        while (parent && parent !== document.body) {
            const linksInParent = parent.querySelectorAll(NAV_LINK_SELECTOR);
            if (linksInParent.length === navLinks.length) {
                applyStyles(parent);
            }
            parent = parent.parentElement;
        }
    }
    
    // Initialize - run immediately and on load
    hideDesignPages();
    alignNavigation();
    
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            hideDesignPages();
            alignNavigation();
        });
    }
    
    // Watch for DOM changes and re-renders - more aggressive checking
    setInterval(function() {
        hideDesignPages();
        alignNavigation();
    }, 100);
    
    new MutationObserver(function() {
        setTimeout(function() {
            hideDesignPages();
            alignNavigation();
        }, 10);
    }).observe(document.body, {childList: true, subtree: true, attributes: true});
    
    // Also run immediately multiple times to catch any late-loading elements
    setTimeout(function() { hideDesignPages(); alignNavigation(); }, 0);
    setTimeout(function() { hideDesignPages(); alignNavigation(); }, 50);
    setTimeout(function() { hideDesignPages(); alignNavigation(); }, 100);
    setTimeout(function() { hideDesignPages(); alignNavigation(); }, 200);
    setTimeout(function() { hideDesignPages(); alignNavigation(); }, 500);
})();
</script>
"""

st.markdown(NAV_STYLES + NAV_SCRIPT, unsafe_allow_html=True)

# Define pages for navigation
# Include all pages in navigation system (required for st.switch_page to work)
# But only show Home in the navigation bar (Story is accessible from Learn More section)
# Note: The first page in the list will be the default page when app loads
try:
    pages = [
        st.Page("pages/intro.py", title="Home", icon="🏠"),  # Default home page (first in list)
        # These pages are registered but accessed via cards, not shown in nav
        st.Page("pages/map_explorer.py", title="Interactive Map Explorer", icon="🗺️"),
        st.Page("pages/trend_comparison.py", title="Time Series Comparison", icon="📊"),
        st.Page("pages/affordability_finder.py", title="Price Affordability Finder", icon="💰"),
        st.Page("pages/story.py", title="Story", icon="📖"),
    ]

    # Create navigation at the top
    # The first page (intro.py) will be the default landing page
    pg = st.navigation(pages, position="top")
    pg.run()
except Exception as e:
    st.error(f"❌ **Application Error**: {str(e)}")
    st.exception(e)
    st.info("""
    **Troubleshooting Steps:**
    1. Check that all page files exist in the `pages/` directory
    2. Verify that all required dependencies are installed
    3. Check the Streamlit Cloud logs for more details
    """)
