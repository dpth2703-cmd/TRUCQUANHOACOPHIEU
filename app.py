import streamlit as st
import yfinance as yf
import pandas as pd
import pymannkendall as mk
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="Mann-Kendall Trend Test",
    page_icon="📈",
    layout="wide"
)

st.title("📈 Mann-Kendall Trend Test")

# ===========================
# Sidebar
# ===========================

st.sidebar.header("Thông tin")

ticker = st.sidebar.text_input("Mã cổ phiếu", "VCB.VN")

start_date = st.sidebar.date_input(
    "Ngày bắt đầu",
    pd.to_datetime("2024-01-01")
)

end_date = st.sidebar.date_input(
    "Ngày kết thúc",
    pd.to_datetime("2026-06-27")
)

run = st.sidebar.button("Kiểm định")

# ===========================
# Main
# ===========================

if run:

    with st.spinner("Đang tải dữ liệu..."):

        df = yf.download(
            ticker,
            start=start_date,
            end=end_date,
            progress=False
        )

    if df.empty:
        st.error("Không có dữ liệu.")
        st.stop()

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.droplevel("Ticker")

    close = df["Close"]

    # -----------------------
    # Chart
    # -----------------------

    fig, ax = plt.subplots(figsize=(12,5))

    ax.plot(close.index, close.values,
            color="royalblue",
            linewidth=2)

    ax.set_title(f"Giá đóng cửa {ticker}")
    ax.grid(True)

    st.pyplot(fig)

    # -----------------------
    # Mann-Kendall
    # -----------------------

    result = mk.original_test(close)

    st.subheader("Kết quả")

    c1, c2, c3 = st.columns(3)

    c1.metric("Trend", result.trend)
    c2.metric("p-value", f"{result.p:.6f}")
    c3.metric("Tau", f"{result.Tau:.4f}")

    c4, c5, c6 = st.columns(3)

    c4.metric("S", result.s)
    c5.metric("Var(S)", f"{result.var_s:.2f}")
    c6.metric("Z", f"{result.z:.4f}")

    # -----------------------
    # Conclusion
    # -----------------------

    st.subheader("Kết luận")

    if result.p < 0.05:

        if result.trend == "increasing":
            st.success("📈 Giá cổ phiếu có xu hướng TĂNG có ý nghĩa thống kê.")

        elif result.trend == "decreasing":
            st.error("📉 Giá cổ phiếu có xu hướng GIẢM có ý nghĩa thống kê.")

        else:
            st.info("Có xu hướng nhưng không xác định được chiều.")

    else:
        st.warning("Không phát hiện xu hướng có ý nghĩa thống kê.")

    # -----------------------
    # Data
    # -----------------------

    st.subheader("Dữ liệu")

    st.dataframe(df, use_container_width=True)

    csv = df.to_csv().encode("utf-8")

    st.download_button(
        "📥 Tải dữ liệu CSV",
        csv,
        file_name=f"{ticker}.csv",
        mime="text/csv"
    )
