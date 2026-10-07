from flask import Flask, request, abort, url_for, render_template_string
import html

app = Flask(__name__)

STUDENTS = {
    "23T1020001": {"name": "Nguyễn Văn An", "lop": "K47A", "scores": {"PMMNM": 8.5, "CSDL": 7.0, "MMT": 9.0}},
    "23T1020002": {"name": "Trần Thị Bình", "lop": "K47A", "scores": {"PMMNM": 6.0, "CSDL": 5.5, "MMT": 7.0}},
    "23T1020003": {"name": "Lê Hoàng Cường", "lop": "K47B", "scores": {"PMMNM": 9.5, "CSDL": 9.0}},
    "23T1020004": {"name": "Phạm Minh Dũng", "lop": "K47B", "scores": {"PMMNM": 4.0, "CSDL": 3.5, "MMT": 5.0}},
    "23T1020005": {"name": "Hoàng Thu Hà", "lop": "K47A", "scores": {}},
    "23T1020006": {"name": "Võ Quốc Khánh", "lop": "K47C", "scores": {"PMMNM": 7.5, "MMT": 8.0}},
}

def average(scores):
    if not scores: return None
    return round(sum(scores.values()) / len(scores), 2)

def rank(avg):
    if avg is None: return "Chưa có điểm"
    if avg >= 8.5: return "Giỏi"
    if avg >= 7.0: return "Khá"
    if avg >= 5.0: return "Trung bình"
    return "Yếu"

def student_summary(mssv):
    student = STUDENTS.get(mssv)
    if not student: return None
    avg = average(student["scores"])
    return {
        "mssv": mssv, "name": student["name"], "lop": student["lop"],
        "scores": student["scores"], "average": avg, "rank": rank(avg)
    }

def layout(title, body):
    escaped_title = html.escape(title)
    return f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>{escaped_title} - Sổ điểm</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-light">
    <nav class="navbar navbar-expand navbar-dark bg-primary mb-4">
        <div class="container">
            <a class="navbar-brand fw-bold" href="{url_for('home')}">Sổ Điểm</a>
            <div class="navbar-nav">
                <a class="nav-link" href="{url_for('home')}">Trang chủ</a>
                <a class="nav-link" href="{url_for('get_students')}">Sinh viên</a>
                <a class="nav-link" href="{url_for('search')}">Tìm kiếm</a>
            </div>
        </div>
    </nav>
    <div class="container">{body}</div>
</body>
</html>"""

@app.route("/")
def home():
    body = f"<h2>Tổng quan Sổ Điểm</h2><p>Tổng số sinh viên: {len(STUDENTS)}</p>"
    return layout("Trang chủ", body)

@app.route("/students")
def get_students():
    summaries = [student_summary(m) for m in STUDENTS.keys()]
    rows = ""
    for s in summaries:
        avg = s["average"] if s["average"] is not None else "N/A"
        rows += f"""<tr>
            <td>{s['mssv']}</td><td>{s['name']}</td><td>{s['lop']}</td>
            <td>{avg}</td><td><span class="badge bg-primary">{s['rank']}</span></td>
            <td><a href="{url_for('get_student_detail', mssv=s['mssv'])}" class="btn btn-sm btn-info text-white">Xem</a></td>
        </tr>"""
    body = f"""<h3>Danh Sách Sinh Viên</h3>
    <table class="table table-striped">
        <thead><tr><th>Mã SV</th><th>Họ tên</th><th>Lớp</th><th>ĐTB</th><th>Xếp loại</th><th>Thao tác</th></tr></thead>
        <tbody>{rows}</tbody>
    </table>"""
    return layout("Danh sách sinh viên", body)

@app.route("/students/<string:mssv>")
def get_student_detail(mssv):
    s = student_summary(mssv)
    if not s: abort(404)
    avg = s["average"] if s["average"] is not None else "Chưa có điểm"
    body = f"""<div class="card p-4">
        <h4>Thông Tin Sinh Viên: {s['name']}</h4>
        <p><strong>Mã SV:</strong> {s['mssv']}</p>
        <p><strong>Lớp:</strong> {s['lop']}</p>
        <p><strong>ĐTB:</strong> {avg}</p>
        <p><strong>Xếp loại:</strong> {s['rank']}</p>
        <a href="{url_for('get_students')}" class="btn btn-secondary">Quay lại</a>
    </div>"""
    return layout("Chi tiết sinh viên", body)

@app.route("/search")
def search():
    q = request.args.get("q", "").strip()
    results = [student_summary(m) for m in STUDENTS.keys() if q.lower() in m.lower() or q.lower() in STUDENTS[m]["name"].lower()] if q else []
    rows = "".join([f"<tr><td>{s['mssv']}</td><td>{s['name']}</td><td>{s['lop']}</td><td>{s['rank']}</td></tr>" for s in results])
    body = f"""<h3>Tìm Kiếm Sinh Viên</h3>
    <form method="GET" action="{url_for('search')}" class="mb-3 d-flex gap-2">
        <input type="text" name="q" class="form-control" placeholder="Nhập tên hoặc mã SV..." value="{html.escape(q)}">
        <button class="btn btn-primary">Tìm</button>
    </form>
    {"<table class='table'><thead><tr><th>Mã SV</th><th>Họ tên</th><th>Lớp</th><th>Xếp loại</th></tr></thead><tbody>" + rows + "</table>" if q else ""}"""
    return layout("Tìm kiếm", body)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)