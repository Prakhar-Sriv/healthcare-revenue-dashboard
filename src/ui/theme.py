def apply_theme():

    import streamlit as st
    import plotly.io as pio

    st.markdown(
        """
        <style>

        /* MAIN BACKGROUND */
        .stApp {
            background: radial-gradient(circle at 20% 20%, #0f2027, #020617 60%);
            color: #e2e8f0;
        }

        /* SIDEBAR */
        section[data-testid="stSidebar"] {
            background: rgba(2, 6, 23, 0.95);
            border-right: 1px solid rgba(255,255,255,0.05);
            backdrop-filter: blur(12px);
        }

        section[data-testid="stSidebar"] * {
            color: #cbd5f5;
        }

        /* METRIC CARDS */
        div[data-testid="metric-container"] {
            background: linear-gradient(145deg, rgba(30,41,59,0.6), rgba(2,6,23,0.6));
            border: 1px solid rgba(255,255,255,0.08);
            padding: 18px;
            border-radius: 18px;
            backdrop-filter: blur(14px);
            box-shadow: 0px 8px 30px rgba(0,0,0,0.7);
            transition: all 0.3s ease;
        }

        div[data-testid="metric-container"]:hover {
            transform: translateY(-5px) scale(1.02);
            border: 1px solid rgba(59,130,246,0.7);
            box-shadow: 0px 12px 40px rgba(59,130,246,0.4);
        }

        /* CHART CARDS */
        .stPlotlyChart {
            background: linear-gradient(145deg, rgba(30,41,59,0.5), rgba(2,6,23,0.5));
            border: 1px solid rgba(255,255,255,0.05);
            border-radius: 18px;
            padding: 12px;
            backdrop-filter: blur(12px);
            box-shadow: 0px 6px 25px rgba(0,0,0,0.6);
            transition: all 0.3s ease;
        }

        .stPlotlyChart:hover {
            box-shadow: 0px 10px 35px rgba(59,130,246,0.25);
        }

        /* BUTTONS */
        .stButton button {
            background: linear-gradient(135deg,#3b82f6,#2563eb);
            color: white;
            border-radius: 12px;
            height: 3em;
            font-weight: 600;
            border: none;
            transition: all 0.25s ease;
        }

        .stButton button:hover {
            transform: translateY(-2px);
            box-shadow: 0px 6px 20px rgba(37,99,235,0.5);
        }

        /* INPUT */
        .stTextInput input {
            background-color: rgba(30,41,59,0.5);
            color: #e2e8f0;
            border-radius: 10px;
            border: 1px solid rgba(255,255,255,0.08);
        }

        /* SELECT BOX */
        .stSelectbox div[data-baseweb="select"] {
            background-color: rgba(30,41,59,0.5);
            border-radius: 10px;
            border: 1px solid rgba(255,255,255,0.08);
        }

        /* DATAFRAME */
        .stDataFrame {
            background-color: rgba(30,41,59,0.4);
            border-radius: 12px;
            border: 1px solid rgba(255,255,255,0.05);
        }

        /* HEADINGS */
        h1, h2, h3, h4 {
            color: #f8fafc;
            font-weight: 600;
        }

        /* DIVIDER */
        hr {
            border-color: rgba(255,255,255,0.05);
        }

        /* SCROLLBAR */
        ::-webkit-scrollbar {
            width: 6px;
        }

        ::-webkit-scrollbar-thumb {
            background: rgba(100,116,139,0.6);
            border-radius: 10px;
        }

        </style>
        """,
        unsafe_allow_html=True
    )

    pio.templates.default = "plotly_dark"


def style_chart(fig):
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=40, b=10),
        font=dict(color="#e2e8f0")
    )
    return fig