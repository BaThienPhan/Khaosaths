# File: khaosat.py

import streamlit as st
import pandas as pd
import os
import qrcode
from io import BytesIO
from PIL import Image
from streamlit_autorefresh import st_autorefresh

# --- CẤU HÌNH CHUNG ---
st.set_page_config(page_title="Khảo sát Kỹ năng",
                   page_icon="🧠", layout="centered")

# Tự động làm mới toàn bộ trang sau mỗi 10 giây để cập nhật kết quả
st_autorefresh(interval=10000, key="global_refresh")

# File dữ liệu
VOTE_FILE = "votes.csv"

# Danh sách câu hỏi
yes_no_questions = [
    "1. Khi bạn bè rủ rê làm điều không muốn, em có thấy khó xử khi từ chối không?",
    "2. Đã bao giờ em làm điều trái ý mình chỉ vì sợ mất lòng bạn bè?",
    "3. Khi đứng trước một lời rủ rê, em có tự tin phân biệt điều đúng – sai hay không?",
    "4. Em có biết cách nói “Không” mà vẫn giữ được sự tôn trọng và mối quan hệ với người khác?",
    "5. Em có muốn học cách từ chối mạnh mẽ, rõ ràng nhưng vẫn tinh tế, không làm người khác buồn?",
    "6. Em có biết nên làm gì để giữ an toàn khi phải đi một mình ở nơi vắng người?",
    "7. Khi ai đó khiến em thấy không thoải mái bằng lời nói hay hành động, em có đủ dũng cảm để lên tiếng không?",
    "8. Nếu cảm thấy lo lắng, bất an, khi rơi vào tình huống nguy hiểm, em thường tìm đến ai để chia sẻ và nhờ hỗ trợ?",
]
text_questions = [
    "9. Đã bao giờ em rơi vào tình huống bị bắt nạt hoặc đe dọa chưa? Lúc đó em xử lý thế nào?",
    "10. Em có mong muốn được học thêm về kỹ năng tự vệ không? Vì sao em cho rằng việc học kỹ năng này là cần thiết (hoặc không cần thiết) trong cuộc sống hàng ngày?",
]

# Tên cột trong file CSV
column_names = [
    f"Q{i+1}" for i in range(len(yes_no_questions))] + ["Q9_text", "Q10_text"]

# Hàm khởi tạo file dữ liệu


def initialize_data_file():
    if not os.path.exists(VOTE_FILE):
        df_init = pd.DataFrame(columns=column_names)
        df_init.to_csv(VOTE_FILE, index=False, encoding='utf-8-sig')

# --- GIAO DIỆN CHÍNH ---


initialize_data_file()

st.title("🧠 Khảo sát: Kỹ năng nói 'Không' và Tự vệ")

# Tạo các tab
tab1, tab2, tab3 = st.tabs(
    ["📝 Thực hiện Khảo sát", "📊 Kết quả Trắc nghiệm", "🗣️ Phản hồi Tự luận"])

# --- TAB 1: THỰC HIỆN KHẢO SÁT ---
with tab1:
    st.header("Điền thông tin khảo sát")

    # QR Code truy cập
    with st.expander("📱 Quét mã QR để bạn bè cùng tham gia"):
        # Thay bằng URL thật của bạn khi deploy
        url = "https://surveyssss.streamlit.app/"
        qr = qrcode.make(url)
        buf = BytesIO()
        qr.save(buf)
        buf.seek(0)
        st.image(Image.open(buf), width=180)

    st.divider()

    # Form phản hồi
    if "submitted" not in st.session_state:
        st.session_state.submitted = False

    if not st.session_state.submitted:
        with st.form("survey_form"):
            st.subheader("Phần 1: Trắc nghiệm")
            user_yes_no_votes = []
            for i, q in enumerate(yes_no_questions):
                vote = st.radio(q, ["✅ Có", "❌ Không"],
                                key=f"q{i}", index=None, horizontal=True)
                user_yes_no_votes.append(vote)

            st.subheader("Phần 2: Tự luận")
            text_answer_9 = st.text_area(
                text_questions[0], height=100, key="q9")
            text_answer_10 = st.text_area(
                text_questions[1], height=100, key="q10")

            submitted = st.form_submit_button("📤 Gửi phản hồi")
            if submitted:
                if None in user_yes_no_votes:
                    st.error(
                        "🚨 Vui lòng trả lời tất cả các câu hỏi trắc nghiệm ở Phần 1.")
                else:
                    processed_votes = [
                        "Yes" if v == "✅ Có" else "No" for v in user_yes_no_votes]
                    all_answers = processed_votes + \
                        [text_answer_9, text_answer_10]

                    df_old = pd.read_csv(VOTE_FILE)
                    new_row = pd.DataFrame([all_answers], columns=column_names)
                    df_new = pd.concat([df_old, new_row], ignore_index=True)
                    df_new.to_csv(VOTE_FILE, index=False, encoding='utf-8-sig')

                    st.session_state.submitted = True
                    st.success("🎉 Cảm ơn bạn đã hoàn thành khảo sát!")
                    st.balloons()
                    st.rerun()  # Tải lại trang để hiển thị thông báo đã gửi
    else:
        st.info("✅ Bạn đã gửi phản hồi. Hãy xem kết quả ở các tab bên cạnh.")

    st.divider()
    # Quản lý dữ liệu (Dành cho Admin)
    with st.expander("🔐 Quản lý dữ liệu (Dành cho Quản trị viên)"):
        password = st.text_input(
            "Nhập mật khẩu để xóa dữ liệu", type="password")
        if st.button("🗑️ Xóa toàn bộ dữ liệu"):
            if password == "112233":
                initialize_data_file()  # Tạo lại file rỗng
                st.session_state.submitted = False
                st.success("✅ Đã xóa toàn bộ dữ liệu. Trang sẽ tự làm mới.")
                st.rerun()
            elif password:
                st.error("❌ Mật khẩu không chính xác.")


# --- TAB 2: KẾT QUẢ TRẮC NGHIỆM ---
with tab2:
    st.header("Thống kê câu hỏi trắc nghiệm")
    st.caption("Dữ liệu được cập nhật tự động.")

    try:
        df = pd.read_csv(VOTE_FILE)
        if df.empty:
            st.info("⏳ Chưa có dữ liệu khảo sát.")
        else:
            st.success(f"**Tổng số lượt phản hồi: {len(df)}**")
            st.divider()
            for i, q in enumerate(yes_no_questions):
                col_name = f"Q{i+1}"
                if col_name in df.columns:
                    yes_count = (df[col_name] == "Yes").sum()
                    no_count = (df[col_name] == "No").sum()
                    total = yes_count + no_count

                    if total > 0:
                        yes_percent = round(yes_count / total * 100, 1)
                        st.markdown(f"**{q}**")
                        st.progress(
                            yes_percent / 100, text=f"✅ Có: {yes_percent}% ({yes_count} phiếu)")
                        st.write(
                            f"↳ *Trong đó có **{no_count}** phiếu trả lời 'Không'.*")
                        st.markdown("---")
    except FileNotFoundError:
        st.info("⏳ Chưa có dữ liệu khảo sát. Hãy là người đầu tiên trả lời!")
    except Exception as e:
        st.error(f"Lỗi khi đọc dữ liệu: {e}")

# --- TAB 3: PHẢN HỒI TỰ LUẬN ---
with tab3:
    st.header("Tổng hợp câu trả lời tự luận")
    st.caption("Các câu trả lời được cập nhật tự động.")

    try:
        df = pd.read_csv(VOTE_FILE)
        if df.empty:
            st.info("⏳ Chưa có dữ liệu khảo sát.")
        else:
            # Câu 9
            st.subheader(f"Câu hỏi: {text_questions[0]}")
            answers_q9 = df["Q9_text"].dropna().unique()
            if len(answers_q9) > 0:
                for ans in answers_q9:
                    if str(ans).strip():
                        st.info(f"🗣️ {ans}")
            else:
                st.write("_Chưa có câu trả lời._")

            st.divider()

            # Câu 10
            st.subheader(f"Câu hỏi: {text_questions[1]}")
            answers_q10 = df["Q10_text"].dropna().unique()
            if len(answers_q10) > 0:
                for ans in answers_q10:
                    if str(ans).strip():
                        st.info(f"💡 {ans}")
            else:
                st.write("_Chưa có câu trả lời._")
    except FileNotFoundError:
        st.info("⏳ Chưa có dữ liệu khảo sát. Hãy là người đầu tiên trả lời!")
    except Exception as e:
        st.error(f"Lỗi khi đọc dữ liệu: {e}")
