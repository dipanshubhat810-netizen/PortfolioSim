import streamlit as st

def is_logged_in():
    return getattr(st.user, "is_logged_in", False)

def get_user_data():
    if is_logged_in():
        try:
            return st.user.to_dict()
        except Exception:
            return {}
    return {}

def get_user_name():
    user_data = get_user_data()
    return (
        user_data.get("name")
        or user_data.get("given_name")
        or user_data.get("email")
        or "User"
    )

def get_user_email():
    user_data = get_user_data()
    return user_data.get("email", "No email available")

def require_login():
    if not is_logged_in():
        st.markdown("## 💼 Welcome to PortfolioSim")
        st.info("Please log in with Google to continue.")
        st.button("Login with Google", on_click=st.login)
        st.stop()

def render_sidebar():
    user_name = get_user_name()
    user_email = get_user_email()

    with st.sidebar:
        st.markdown(
            '<div style="font-size:1.6rem;font-weight:800;color:#00d4aa;letter-spacing:-1px;">PortfolioSim</div>',
            unsafe_allow_html=True
        )
        st.markdown(
            '<div style="font-size:0.7rem;color:#64748b;letter-spacing:3px;text-transform:uppercase;">Investment Simulator</div>',
            unsafe_allow_html=True
        )
        st.markdown("---")
        st.markdown(f"**👤 {user_name}**")
        st.markdown(
            f'<span style="color:#64748b;font-size:0.8rem;">{user_email}</span>',
            unsafe_allow_html=True
        )
        st.markdown("---")
        st.markdown(
            '<span style="color:#f59e0b;font-size:0.75rem;">⚠️ Mock Data Mode</span>',
            unsafe_allow_html=True
        )
        st.markdown(
            '<span style="color:#64748b;font-size:0.72rem;">DB: portfolio_sim (not connected)</span>',
            unsafe_allow_html=True
        )

        if st.button("Logout"):
            st.logout()
