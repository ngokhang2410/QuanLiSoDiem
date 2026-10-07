from flask import Flask, url_for, render_template_string
import html

app = Flask(__name__)

# Dữ liệu mẫu chuẩn từ đề bài
STUDENTS = {
    "23T1020001": {"name": "Nguyễn Văn An", "lop": "K47A", "scores": {"PMMNM": 8.5, "CSDL": 7.0, "MMT": 9.0}},
    "23T1020002": {"name": "Trần Thị Bình", "lop": "K47A", "scores": {"PMMNM": 6.0, "CSDL": 5.5, "MMT": 7.0}},
    "23T1020003": {"name": "Lê Hoàng Cường", "lop": "K47B", "scores": {"PMMNM": 9.5, "CSDL": 9.0}},
    "23T1020004": {"name": "Phạm Minh Dũng", "lop": "K47B", "scores": {"PMMNM": 4.0, "CSDL": 3.5, "MMT": 5.0}},
    "23T1020005": {"name": "Hoàng Thu Hà", "lop": "K47A", "scores": {}},
    "23T1020006": {"name": "Võ Quốc Khánh", "lop": "K47C", "scores": {"PMMNM": 7.5, "MMT": 8.0}},
}

def average(scores):
    """Tính trung bình cộng, làm tròn 2 chữ số; dict rỗng -> None"""
    if not scores:
        return None
    return round(sum(scores.values()) / len(scores), 2)

def rank(avg):
    """Xếp loại học lực"""
    if avg is None:
        return "Chưa có điểm"
    if avg >= 8.5:
        return "Giỏi"
    if avg >= 7.0:
        return "Khá"
    if avg >= 5.0:
        return "Trung bình"
    return "Yếu"

def student_summary(mssv):
    """Tạo dict tổng hợp thông tin sinh viên"""
    student = STUDENTS.get(mssv)
    if not student:
        return None
    avg = average(student["scores"])
    rnk = rank(avg)
    return {
        "mssv": mssv,
        "name": student["name"],
        "lop": student["lop"],
        "scores": student["scores"],
        "average": avg,
        "rank": rnk
    }

def layout(title, body):
    """Khung trang HTML sử dụng url_for"""
    escaped_title = html.escape(title)
    return f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>{escaped_title} - Sổ điểm</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <div class="container my-4">
        {body}
    </div>
</body>
</html>"""

@app.route("/")
def home():
    return layout("Trang chủ", "<h1>Sổ Điểm Điện Tử - Khởi tạo thành công Phần 0</h1>")

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)