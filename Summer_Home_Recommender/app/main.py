import streamlit as st
from app.utils.helpers import properties
from app.models.user import User
from app.services.recommender import PropertyRecommender, SearchCriteria
from openai import OpenAI
from app.services.auth import create_user_account, authenticate_user
from app.services.chatbot import ChatbotService

# Configure the page
st.set_page_config(
    page_title="Summer Home Finder",
    page_icon="🏖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize OpenAI client for LLM
@st.cache_resource
def init_llm_client():
    try:
        api_key = st.secrets.get("OPENAI_API_KEY")
        if not api_key:
            st.error("❌ OpenAI API key not configured. Please check your .streamlit/secrets.toml file.")
            return None
        return OpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1",
            timeout=30.0
        )
    except Exception as e:
        st.error(f"❌ Error initializing OpenAI client: {str(e)}")
        return None

client = init_llm_client()

# Check if client was initialized successfully
if client is None:
    st.error("❌ Unable to initialize AI services. Please check your API key configuration.")
    st.stop()

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'current_user' not in st.session_state:
    st.session_state.current_user = None
if 'search_criteria' not in st.session_state:
    st.session_state.search_criteria = {}
if 'recommendations' not in st.session_state:
    st.session_state.recommendations = None
if 'recommender' not in st.session_state:
    st.session_state.recommender = None
if 'show_profile_edit' not in st.session_state:
    st.session_state.show_profile_edit = False


def initialize_recommender():
    """Initialize the property recommender system"""
    if st.session_state.recommender is None:
        st.session_state.recommender = PropertyRecommender(properties)

def get_recommendations(search_criteria, selected_features):
    """Get property recommendations using the recommender system"""
    try: 
        # Initialize recommender
        initialize_recommender()
        
        # Create SearchCriteria object
        criteria = SearchCriteria(
            group_size=search_criteria['group_size'],
            preferred_environment=search_criteria['preferred_environment'],
            min_budget=search_criteria['min_budget'],
            max_budget=search_criteria['max_budget'],
            location=search_criteria.get('location', ''),
            user_preferences=', '.join(selected_features) if selected_features else ''
        )
        
        # Get recommendations
        recommendations = st.session_state.recommender.get_detailed_recommendations(criteria, top_k=5)
        return recommendations
        
    except Exception as e:
        st.error(f"Error getting recommendations: {str(e)}")
        return []

# Initialize chatbot service lazily
@st.cache_resource
def get_chatbot_service():
    """Get or create chatbot service instance"""
    try:
        api_key = st.secrets.get("OPENAI_API_KEY", None)
        if api_key:
            return ChatbotService(api_key=api_key, properties=properties)
        else:
            # Return None if no API key is available
            return None
    except Exception:
        # Return None if secrets are not available
        return None

def profile_edit_view():
    """Dedicated profile editing view"""
    user = st.session_state.current_user
    
    # Sidebar for navigation and user info
    with st.sidebar:
        st.header("👤 Your Profile")
        st.write(f"**Name:** {user.name}")
        st.write(f"**Email:** {user.email}")
        st.write(f"**User ID:** {user.user_id[:8]}...")
        
        st.markdown("---")
        
        if st.button("🏠 Back to Main App", type="primary", use_container_width=True):
            st.session_state.show_profile_edit = False
            st.rerun()
        
        if st.button("🚪 Logout", type="secondary", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.current_user = None
            st.rerun()
    
    # Header - clean title only
    st.title("👤 Edit Profile")
    st.write("Update your profile information and password")
    
    st.markdown("---")
    
    # Profile information display
    st.subheader("📋 Current Profile Information")
    
    # Create a nice profile card
    with st.container():
        st.markdown("""
        <div style="background-color: #f0f2f6; padding: 20px; border-radius: 10px; border-left: 4px solid #1f77b4;">
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**👤 Name:** {user.name}")
            st.write(f"**📧 Email:** {user.email}")
        with col2:
            st.write(f"**🆔 User ID:** {user.user_id}")
            st.write(f"**🔑 Password:** {'*' * len(user.password) if user.password else 'Not set'}")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Profile editing form
    st.subheader("✏️ Edit Profile Information")
    st.info("💡 You can update your name and/or password. Leave password fields blank to keep your current password.")
    
    with st.form("edit_profile"):
        new_name = st.text_input("👤 Full Name", value=user.name, help="Enter your new full name")
        
        st.write("**🔑 Change Password (leave blank to keep current password)**")
        
        # Show password requirements
        with st.expander("🔒 Password Requirements", expanded=False):
            st.write("Your new password must meet the following criteria:")
            st.write("✅ At least 8 characters long")
            st.write("✅ At least one uppercase letter (A-Z)")
            st.write("✅ At least one lowercase letter (a-z)")
            st.write("✅ At least one number (0-9)")
            st.write("✅ At least one symbol (!@#$%^&* etc.)")
        
        new_password = st.text_input("🔑 New Password", type="password", placeholder="Enter new password (optional)")
        confirm_password = st.text_input("🔐 Confirm New Password", type="password", placeholder="Confirm new password")
        
        # Password strength indicator for new password
        if new_password:
            is_valid, message = User.validate_password(new_password)
            if is_valid:
                st.success(f"✅ {message}")
            else:
                st.error(f"❌ {message}")
        
        # Password confirmation check
        if new_password and confirm_password and new_password != confirm_password:
            st.error("❌ New passwords do not match!")
        elif new_password and confirm_password and new_password == confirm_password:
            if User.validate_password(new_password)[0]:
                st.success("✅ New passwords match and meet requirements!")
            else:
                st.error("❌ New password does not meet requirements")
        
        # Form buttons with better spacing
        st.write("")  # Add some space
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            if st.form_submit_button("💾 Save Changes", type="primary", use_container_width=True):
                try:
                    changes_made = False
                    
                    # Update name if changed
                    if new_name != user.name:
                        user.update_profile(name=new_name)
                        changes_made = True
                    
                    # Update password if provided
                    if new_password and confirm_password and new_password == confirm_password:
                        if User.validate_password(new_password)[0]:
                            user.update_profile(password=new_password)
                            changes_made = True
                    
                    if changes_made:
                        # Refresh session state
                        st.session_state.current_user = user
                        st.success("✅ Profile updated successfully!")
                        # Auto-hide the edit form after a short delay
                        st.session_state.show_profile_edit = False
                        st.rerun()
                    else:
                        st.info("ℹ️ No changes were made to your profile.")
                    
                except Exception as e:
                    st.error(f"❌ Error updating profile: {str(e)}")
        
        with col2:
            if st.form_submit_button("❌ Cancel", type="secondary", use_container_width=True):
                st.session_state.show_profile_edit = False
                st.rerun()
        
        with col3:
            if st.form_submit_button("🔄 Reset to Current", type="secondary", use_container_width=True):
                st.rerun()
    
    # Footer with additional navigation
    st.markdown("---")
    st.write("💡 **Tip:** Use the sidebar to quickly navigate back to the main app or edit your profile.")


# Main app layout
def main_app():
    # Header - clean title only
    st.title("🏖️ Summer Home Finder")
    st.write("Find your perfect summer getaway with our amazing recommender system!")
    
    # Sidebar for user info and navigation
    with st.sidebar:
        st.header("👤 Your Profile")
        user = st.session_state.current_user
        st.write(f"**Name:** {user.name}")
        st.write(f"**Email:** {user.email}")
        st.write(f"**User ID:** {user.user_id[:8]}...")
        
        if st.button("✏️ Edit Profile", type="secondary", use_container_width=True):
            st.session_state.show_profile_edit = True
            st.rerun()
            
        if st.button("🚪 Logout", type="secondary", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.current_user = None
            st.rerun()
    
    # Main content tabs
    tab1, tab2 = st.tabs(["🔍 Search", "🤖 Chatbot"])
    
    with tab1:
        st.header("Search Criteria")
        
        col1, col2 = st.columns(2)
        
        with col1:
            group_size = st.number_input(
                "👥 Group Size",
                min_value=1,
                max_value=20,
                value=st.session_state.search_criteria.get('group_size', 2),
                help="How many people will be staying?"
            )
            
            preferred_environment = st.selectbox(
                "🌍 Preferred Environment",
                ["mountain", "lake", "beach", "city"],
                index=["mountain", "lake", "beach", "city"].index(st.session_state.search_criteria.get('preferred_environment', 'beach'))
            )
        
        with col2:
            budget_col1, budget_col2 = st.columns(2)
            with budget_col1:
                min_budget = st.number_input(
                    "💰 Min Budget (per night)",
                    min_value=50,
                    max_value=2000,
                    value=st.session_state.search_criteria.get('min_budget', 100),
                    step=50
                )
                # Location search bar
                location_input = st.text_input(
                    "📍 Location",
                    placeholder="Enter the name of a city",
                    value=st.session_state.search_criteria.get('location', ''),
                    help="Enter a specific city or location you'd like to visit"
                )
            with budget_col2:
                max_budget = st.number_input(
                    "💰 Max Budget (per night)",
                    min_value=min_budget,
                    max_value=2000,
                    value=st.session_state.search_criteria.get('max_budget', 500),
                    step=50
                )
        
        # Add preferences selection fields
        st.subheader("🎯 Select Priority Features")
        st.write("Choose up to 3 features that are most important to you:")
        
        # Get all available features from properties
        all_features = set()
        for prop in properties:
            all_features.update(prop.features)
        
        # Sort features for better UX
        sorted_features = sorted(list(all_features))
        
        # Initialize selected preferences in session state if not exists
        if 'selected_preferences' not in st.session_state:
            st.session_state.selected_preferences = []
        
        # Show count of selected features
        st.write(f"**Selected: {len(st.session_state.selected_preferences)}/3 features**")
        
        # Create toggle buttons in a grid (4 columns for better layout)
        cols = st.columns(4)
        for i, feature in enumerate(sorted_features):
            col_idx = i % 4
            with cols[col_idx]:
                is_selected = feature in st.session_state.selected_preferences
                can_select = len(st.session_state.selected_preferences) < 3 or is_selected
                
                if st.button(
                    feature,
                    type="primary" if is_selected else "secondary",
                    disabled=not can_select,
                    key=f"toggle_{feature}",
                    help="Click to select/deselect this feature"
                ):
                    # Toggle selection logic
                    if feature in st.session_state.selected_preferences:
                        st.session_state.selected_preferences.remove(feature)
                    else:
                        st.session_state.selected_preferences.append(feature)
                    st.rerun()
        
        # Show selected preferences
        if st.session_state.selected_preferences:
            st.success(f"**Selected Features:** {', '.join(st.session_state.selected_preferences)}")
        else:
            st.info("💡 Click on features to select them (up to 3)")
        
        # Search button
        if st.button("🔍 Search", type="primary"):
            # Update search criteria
            st.session_state.search_criteria = {
                'group_size': group_size,
                'preferred_environment': preferred_environment,
                'min_budget': min_budget,
                'max_budget': max_budget,
                'location': location_input,
                'selected_features': st.session_state.selected_preferences
            }
            
            # Get recommendations
            with st.spinner("🔍 Finding your perfect matches..."):
                recommendations = get_recommendations(st.session_state.search_criteria, st.session_state.selected_preferences)
                st.session_state.recommendations = recommendations
                st.success(f"✅ Found {len(recommendations)} properties matching your criteria!")
                st.rerun()
        
        # Display recommendations if available
        if st.session_state.recommendations:
            st.subheader("🏠 Your Personalized Recommendations")
            
            # Display current search criteria
            st.info(f"**Search Criteria:** {st.session_state.search_criteria['group_size']} people, {st.session_state.search_criteria['preferred_environment']} environment, {st.session_state.search_criteria['location'] if st.session_state.search_criteria['location'] else 'Any location'}, ${st.session_state.search_criteria['min_budget']}-${st.session_state.search_criteria['max_budget']}/night")
            
            # Display recommendations
            for i, rec in enumerate(st.session_state.recommendations, 1):
                prop = rec['property']
                overall_score = rec['overall_score']
                
                with st.expander(f"🏠 {i}. {prop.property_id} - {prop.location} {prop.property_type} - ${prop.price_per_night}/night (Score: {overall_score:.3f})"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**📍 Location:** {prop.location}")
                        st.write(f"**🏠 Type:** {prop.property_type.title()}")
                        st.write(f"**💰 Price:** ${prop.price_per_night}/night")
                        st.write(f"**🛏️ Bedrooms:** {prop.bedrooms}")
                        st.write(f"**✨ Features:** {', '.join(prop.features)}")
                        st.write(f"**🏷️ Tags:** {', '.join(prop.tags)}")
                    
                    with col2:
                        st.write("**📊 Score Breakdown:**")
                        breakdown = rec['score_breakdown']
                        for criterion, details in breakdown.items():
                            st.write(f"   {criterion.title()}: {details['score']:.3f} (weight: {details['weight']:.1%})")
                        
                        # Show why this property was recommended
                        st.write("**🎯 Why Recommended:**")
                        if breakdown['budget']['score'] > 0.8:
                            st.write("   ✅ Great value for your budget")
                        if breakdown['environment']['score'] > 0.8:
                            st.write("   ✅ Perfect environment match")
                        if breakdown['features']['score'] > 0.7:
                            st.write("   ✅ Matches your preferences")
    
    with tab2:
        st.header("🤖 AI-Powered Location Discovery")
        st.write("Chat with our AI to discover the perfect location for your summer home! Describe your preferences and get personalized location recommendations.")
        
        # Initialize chatbot session state
        if 'chatbot_messages' not in st.session_state:
            st.session_state.chatbot_messages = []
        
        if 'chatbot_location_recommendation' not in st.session_state:
            st.session_state.chatbot_location_recommendation = None
        
        # Display chat history
        st.subheader("💬 Conversation History")
        chat_container = st.container()
        
        with chat_container:
            for message in st.session_state.chatbot_messages:
                if message["role"] == "user":
                    st.chat_message("user").write(message["content"])
                else:
                    st.chat_message("assistant").write(message["content"])
        
        # Display location recommendation if available
        if st.session_state.chatbot_location_recommendation:
            st.subheader("🎯 Your Recommended Location")
            location_info = st.session_state.chatbot_location_recommendation
            
            with st.expander(f"🏠 Property #{location_info['property_id']} - 📍 {location_info['location']} - {location_info['reasoning']}", expanded=True):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**🏠 Location:** {location_info['location']}")
                    st.write(f"**🏠 Property Type:** {location_info['property_type']}")
                    st.write(f"**💰 Price:** ${location_info['price_per_night']}/night")
                with col2:
                    st.write(f"**✨ Key Features:** {', '.join(location_info['features'][:3])}")
                    st.write(f"**🏷️ Tags:** {', '.join(location_info['tags'][:3])}")
                    st.write(f"**🛏️ Bedrooms:** {location_info['bedrooms']}")
                
                st.success("💡 **Tip:** Use the Search tab to find specific properties in this location!")
        
        # Chat input
        st.subheader("💭 Start a New Conversation")
        user_input = st.text_area(
            "Describe what you're looking for:",
            placeholder="e.g., I want a peaceful mountain retreat for my family of 4, with hiking trails nearby, budget around $200-300 per night, and I need wifi for remote work...",
            height=100,
            key="chatbot_input"
        )
        
        col1, col2 = st.columns([3, 1])
        with col1:
            if st.button("🚀 Get Location Recommendation", type="primary", use_container_width=True):
                if user_input:
                    with st.spinner("🤖 AI is analyzing your preferences and finding the perfect location..."):
                        # Add user message to chat
                        st.session_state.chatbot_messages.append({"role": "user", "content": user_input})
                        
                        # Get AI recommendation
                        chatbot_service = get_chatbot_service()
                        if chatbot_service:
                            location_rec = chatbot_service.get_location_recommendation(user_input)
                        else:
                            location_rec = None
                            st.error("❌ AI chatbot service is not configured. Please check your .streamlit/secrets.toml file and ensure OPENAI_API_KEY is set.")
                        
                        if location_rec:
                            # Add AI response to chat
                            ai_response = f"I've analyzed your preferences and found the perfect property for you! **{location_rec['property_type'].title()} in {location_rec['location']}** - ${location_rec['price_per_night']}/night with {location_rec['bedrooms']} bedrooms.\n\n**Features:** {', '.join(location_rec['features'][:3])}\n**Tags:** {', '.join(location_rec['tags'][:3])}\n\n**Why this property is perfect for you:**\n{location_rec['reasoning']}"
                            
                            st.session_state.chatbot_messages.append({"role": "assistant", "content": ai_response})
                            st.session_state.chatbot_location_recommendation = location_rec
                            
                            st.success("✅ Location recommendation generated! Check the conversation above.")
                            st.rerun()
                        else:
                            st.error("❌ Unable to generate location recommendation. Please try again with more specific details.")
                else:
                    st.warning("⚠️ Please describe your preferences first.")
        
        with col2:
            if st.button("🗑️ Clear Chat", type="secondary", use_container_width=True):
                st.session_state.chatbot_messages = []
                st.session_state.chatbot_location_recommendation = None
                st.rerun()
        
        # Help text
        with st.expander("💡 How to get the best property recommendations", expanded=False):
            st.write("""
            **For the best property recommendations, try to include:**
            - 👥 **Group size** (how many people - we'll match with available bedrooms)
            - 🌍 **Location preference** (city, region, or specific area)
            - 💰 **Budget range** (per night)
            - 🎯 **Specific features** (pool, ocean view, mountain view, etc.)
            - 🏠 **Property type** (house, apartment, villa, cabin, etc.)
            - 🏖️ **Environment** (beach, mountain, lake, city, etc.)
            
            **Example:** "I'm looking for a beachfront villa for 6 people, budget $400-600 per night, with a pool and ocean views, somewhere warm and tropical."
            """)


# Authentication UI
def auth_ui():
    st.title("🏖️ Welcome to Summer Home Finder")
    st.write("Please create an account or login to continue")
    
    tab1, tab2 = st.tabs(["🆕 Create Account", "🔑 Login"])
    
    with tab1:
        st.header("Create New Account")
        
        # Display password requirements
        with st.expander("🔒 Password Requirements", expanded=False):
            st.write("Your password must meet the following criteria:")
            st.write("✅ At least 8 characters long")
            st.write("✅ At least one uppercase letter (A-Z)")
            st.write("✅ At least one lowercase letter (a-z)")
            st.write("✅ At least one number (0-9)")
            st.write("✅ At least one symbol (!@#$%^&* etc.)")
        
        with st.form("create_account"):
            name = st.text_input("👤 Full Name", placeholder="Enter your full name")
            email = st.text_input("📧 Email", placeholder="Enter your email address")
            password = st.text_input("🔑 Password", type="password", placeholder="Enter your password")
            
            # Password strength indicator
            if password:
                is_valid, message = User.validate_password(password)
                if is_valid:
                    st.success(f"✅ {message}")
                else:
                    st.error(f"❌ {message}")
            
            confirm_password = st.text_input("🔐 Confirm Password", type="password", placeholder="Confirm your password")
            
            # Password confirmation check
            if confirm_password and password != confirm_password:
                st.error("❌ Passwords do not match!")
            elif confirm_password and password == confirm_password and password:
                if User.validate_password(password)[0]:
                    st.success("✅ Passwords match and meet requirements!")
                else:
                    st.error("❌ Password does not meet requirements")
            
            submitted = st.form_submit_button("🚀 Create Account", type="primary")
            
            if submitted:
                if name and email and password and confirm_password:
                    # Check if passwords match
                    if password != confirm_password:
                        st.error("❌ Passwords do not match!")
                    else:
                        # Check if email already exists
                        existing_user = User.find_by_email(email)
                        if existing_user:
                            st.error("❌ An account with this email already exists. Please login instead.")
                        else:
                            user, message = create_user_account(name, email, password)
                            if user:
                                st.session_state.authenticated = True
                                st.session_state.current_user = user
                                st.success(f"✅ Account created successfully! Welcome, {name}!")
                                st.rerun()
                            else:
                                st.error(f"❌ {message}")
                else:
                    st.error("❌ Please fill in all fields.")
    
    with tab2:
        st.header("Login to Existing Account")
        with st.form("login"):
            email = st.text_input("📧 Email", placeholder="Enter your email address")
            password = st.text_input("🔑 Password", type="password", placeholder="Enter your password")
            
            submitted = st.form_submit_button("🔑 Login", type="primary")
            
            if submitted:
                if email and password:
                    user = authenticate_user(email, password)
                    if user:
                        st.session_state.authenticated = True
                        st.session_state.current_user = user
                        st.success(f"✅ Welcome back, {user.name}!")
                        st.rerun()
                    else:
                        st.error("❌ Invalid email or password. Please try again.")
                else:
                    st.error("❌ Please enter your email and password.")

# Main app logic
if st.session_state.authenticated:
    if st.session_state.show_profile_edit:
        profile_edit_view()
    else:
        main_app()
else:
    auth_ui()

# Footer
st.markdown("---")
st.markdown("🏖️ **Summer Home Finder** - Created by Team 14 - Purple Martins")
