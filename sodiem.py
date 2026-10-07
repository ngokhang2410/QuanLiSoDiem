from flask import Flask, request, jsonify, abort, make_response, url_for, render_template_string
import html
import io
import csv

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

# -----------------------------------------------------------------------------
# CÁC HÀM PHỤ THEO YÊU CẦU ĐỀ BÀI (CÂU 0.3)
# -----------------------------------------------------------------------------
def average(scores):
    """Tính trung bình cộng, làm tròn 2 chữ số; dict rỗng -> None"""
    if not scores:
        return None
    return round(sum(scores.values()) / len(scores), 2)

def rank(avg):
    """Xếp loại học lực dựa trên điểm trung bình"""
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

# -----------------------------------------------------------------------------
# KHUNG TRANG LAYOUT (CÂU 0.4)
# -----------------------------------------------------------------------------
def layout(title, body):
    """Trang HTML hoàn chỉnh; <title> dạng ... - Sổ điểm; menu sinh bằng url_for"""
    escaped_title = html.escape(title)
    home_url = url_for('home')
    students_url = url_for('get_students')
    search_url = url_for('search')
    api_url = url_for('api_get_students')

    template = f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{escaped_title} - Sổ điểm</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css">
    <style>
        body {{ background-color: #f4f6f9; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }}
        .navbar-brand {{ font-weight: 700; letter-spacing: 0.5px; }}
        .stat-card {{ border: none; border-radius: 12px; transition: all 0.3s ease; }}
        .stat-card:hover {{ transform: translateY(-4px); box-shadow: 0 8px 20px rgba(0,0,0,0.08); }}
        .content-box {{ background: white; border-radius: 12px; padding: 25px; border: 1px solid #e9ecef; box-shadow: 0 2px 8px rgba(0,0,0,0.04); }}
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary shadow-sm mb-4">
        <div class="container">
            <a class="navbar-brand" href="{home_url}"><i class="bi bi-journal-check me-2"></i>Sổ Điểm Điện Tử</a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item">
                        <a class="nav-link" href="{home_url}"><i class="bi bi-house-door me-1"></i>Trang chủ</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="{students_url}"><i class="bi bi-people me-1"></i>Sinh viên</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="{search_url}"><i class="bi bi-search me-1"></i>Tìm kiếm</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="{api_url}" target="_blank"><i class="bi bi-code-slash me-1"></i>API JSON</a>
                    </li>
                </ul>
            </div>
        </div>
    </nav>

    <div class="container mb-5">
        {body}
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>"""
    return template

# -----------------------------------------------------------------------------
# CÁC ROUTE GIAO DIỆN WEB
# -----------------------------------------------------------------------------
@app.route("/")
def home():
    total_students = len(STUDENTS)
    total_classes = len(set(info["lop"] for info in STUDENTS.values()))
    
    body = f"""
    <div class="row mb-4">
        <div class="col-12">
            <h2 class="fw-bold text-dark mb-1">Tổng quan ứng dụng Sổ điểm</h2>
            <p class="text-muted">Hệ thống quản lý điểm thi và danh sách sinh viên trực tuyến</p>
        </div>
    </div>

    <div class="row g-4 mb-4">
        <div class="col-md-6 col-lg-4">
            <div class="card stat-card bg-white p-3 border-start border-primary border-4 shadow-sm">
                <div class="d-flex align-items-center">
                    <div class="rounded-circle bg-primary bg-opacity-10 p-3 me-3">
                        <i class="bi bi-people-fill fs-2 text-primary"></i>
                    </div>
                    <div>
                        <div class="text-muted small">Tổng số sinh viên</div>
                        <div class="fs-3 fw-bold text-dark">{total_students}</div>
                    </div>
                </div>
            </div>
        </div>
        <div class="col-md-6 col-lg-4">
            <div class="card stat-card bg-white p-3 border-start border-success border-4 shadow-sm">
                <div class="d-flex align-items-center">
                    <div class="rounded-circle bg-success bg-opacity-10 p-3 me-3">
                        <i class="bi bi-building fs-2 text-success"></i>
                    </div>
                    <div>
                        <div class="text-muted small">Số lớp học</div>
                        <div class="fs-3 fw-bold text-dark">{total_classes}</div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <div class="content-box">
        <h5 class="fw-bold mb-3"><i class="bi bi-lightning-charge me-2 text-warning"></i>Thao tác nhanh</h5>
        <div class="d-flex flex-wrap gap-2">
            <a href="{url_for('get_students')}" class="btn btn-outline-primary"><i class="bi bi-list-ul me-1"></i>Xem danh sách sinh viên</a>
            <a href="{url_for('get_students')}?export=csv" class="btn btn-outline-success"><i class="bi bi-file-earmark-spreadsheet me-1"></i>Xuất File CSV</a>
            <a href="{url_for('api_get_students')}" class="btn btn-outline-info" target="_blank"><i class="bi bi-json me-1"></i>Xem API JSON</a>
        </div>
    </div>
    """
    return layout("Trang chủ", body)

@app.route("/students")
def get_students():
    export = request.args.get("export")
    
    # Lấy danh sách tổng hợp bằng student_summary
    summaries = [student_summary(mssv) for mssv in STUDENTS.keys()]

    if export == "csv":
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Mã SV", "Họ tên", "Lớp", "Điểm TB", "Xếp loại", "Chi tiết điểm"])
        for s in summaries:
            avg_str = s["average"] if s["average"] is not None else ""
            scores_str = "; ".join([f"{k}: {v}" for k, v in s["scores"].items()]) if s["scores"] else "Chưa có điểm"
            writer.writerow([s["mssv"], s["name"], s["lop"], avg_str, s["rank"], scores_str])
        
        response = make_response(output.getvalue())
        response.headers["Content-Disposition"] = "attachment; filename=danh_sach_sinh_vien.csv"
        response.headers["Content-type"] = "text/csv; charset=utf-8-sig"
        return response

    rows_html = ""
    for s in summaries:
        scores_badges = ""
        if s["scores"]:
            for mon, diem in s["scores"].items():
                scores_badges += f'<span class="badge bg-info bg-opacity-10 text-dark border me-1">{mon}: {diem}</span>'
        else:
            scores_badges = '<span class="text-muted small"><em>Chưa có điểm</em></span>'

        # Hiển thị màu sắc theo xếp loại
        rank_badge_class = "bg-secondary"
        if s["rank"] == "Giỏi": rank_badge_class = "bg-success"
        elif s["rank"] == "Khá": rank_badge_class = "bg-primary"
        elif s["rank"] == "Trung bình": rank_badge_class = "bg-warning text-dark"
        elif s["rank"] == "Yếu": rank_badge_class = "bg-danger"

        avg_disp = s["average"] if s["average"] is not None else "N/A"

        rows_html += f"""
        <tr>
            <td class="ps-4"><span class="badge bg-secondary">{s["mssv"]}</span></td>
            <td class="fw-semibold">{s["name"]}</td>
            <td><span class="badge bg-light text-dark border">{s["lop"]}</span></td>
            <td>{scores_badges}</td>
            <td class="fw-bold text-primary">{avg_disp}</td>
            <td><span class="badge {rank_badge_class}">{s["rank"]}</span></td>
            <td class="text-end pe-4">
                <a href="{url_for('get_student_detail', mssv=s['mssv'])}" class="btn btn-sm btn-outline-primary"><i class="bi bi-eye"></i> Chi tiết</a>
            </td>
        </tr>
        """

    body = f"""
    <div class="d-flex justify-content-between align-items-center mb-4">
        <div>
            <h3 class="fw-bold mb-0">Danh Sách Sinh Viên</h3>
            <p class="text-muted small mb-0">Quản lý và theo dõi điểm trung bình & xếp loại sinh viên</p>
        </div>
        <a href="{url_for('get_students')}?export=csv" class="btn btn-success"><i class="bi bi-download me-1"></i>Xuất CSV</a>
    </div>

    <div class="content-box p-0 overflow-hidden">
        <table class="table table-hover align-middle mb-0">
            <thead class="table-light">
                <tr>
                    <th class="ps-4">Mã SV</th>
                    <th>Họ và tên</th>
                    <th>Lớp</th>
                    <th>Điểm môn học</th>
                    <th>Điểm TB</th>
                    <th>Xếp loại</th>
                    <th class="text-end pe-4">Thao tác</th>
                </tr>
            </thead>
            <tbody>
                {rows_html}
            </tbody>
        </table>
    </div>
    """
    return layout("Danh sách sinh viên", body)

@app.route("/students/<string:mssv>")
def get_student_detail(mssv):
    s = student_summary(mssv)
    if not s:
        abort(404)
        
    rank_badge_class = "bg-secondary"
    if s["rank"] == "Giỏi": rank_badge_class = "bg-success"
    elif s["rank"] == "Khá": rank_badge_class = "bg-primary"
    elif s["rank"] == "Trung bình": rank_badge_class = "bg-warning text-dark"
    elif s["rank"] == "Yếu": rank_badge_class = "bg-danger"

    avg_disp = s["average"] if s["average"] is not None else "Chưa có điểm"

    scores_table = ""
    if s["scores"]:
        scores_rows = "".join([f"<tr><td>{mon}</td><td class='fw-bold text-primary'>{diem}</td></tr>" for mon, diem in s["scores"].items()])
        scores_table = f"""
        <table class="table table-bordered align-middle mt-3">
            <thead class="table-light">
                <tr><th>Môn học</th><th>Điểm số</th></tr>
            </thead>
            <tbody>{scores_rows}</tbody>
        </table>
        """
    else:
        scores_table = '<div class="alert alert-warning mt-3 mb-0">Sinh viên chưa có điểm học phần nào.</div>'

    body = f"""
    <div class="row justify-content-center">
        <div class="col-md-8">
            <div class="content-box">
                <div class="d-flex justify-content-between align-items-center mb-4">
                    <h4 class="fw-bold mb-0">Thông Tin Sinh Viên</h4>
                    <a href="{url_for('get_students')}" class="btn btn-outline-secondary btn-sm"><i class="bi bi-arrow-left"></i> Quay lại</a>
                </div>
                <ul class="list-group list-group-flush mb-4">
                    <li class="list-group-item d-flex justify-content-between py-3">
                        <span class="text-muted">Mã Sinh Viên:</span>
                        <span class="fw-bold">{s["mssv"]}</span>
                    </li>
                    <li class="list-group-item d-flex justify-content-between py-3">
                        <span class="text-muted">Họ và Tên:</span>
                        <span class="fw-bold">{s["name"]}</span>
                    </li>
                    <li class="list-group-item d-flex justify-content-between py-3">
                        <span class="text-muted">Lớp Sinh Hoạt:</span>
                        <span class="fw-bold">{s["lop"]}</span>
                    </li>
                    <li class="list-group-item d-flex justify-content-between py-3">
                        <span class="text-muted">Điểm Trung Bình:</span>
                        <span class="fs-5 fw-bold text-primary">{avg_disp}</span>
                    </li>
                    <li class="list-group-item d-flex justify-content-between py-3">
                        <span class="text-muted">Xếp Loại:</span>
                        <span class="badge {rank_badge_class} fs-6">{s["rank"]}</span>
                    </li>
                </ul>

                <h5 class="fw-bold mb-3"><i class="bi bi-journal-text me-2"></i>Bảng điểm chi tiết</h5>
                {scores_table}
            </div>
        </div>
    </div>
    """
    return layout("Chi tiết sinh viên", body)

@app.route("/search")
def search():
    query = request.args.get("q", "").strip()
    results = []
    if query:
        for mssv in STUDENTS.keys():
            s = student_summary(mssv)
            if query.lower() in s["mssv"].lower() or query.lower() in s["name"].lower():
                results.append(s)

    results_html = ""
    if query:
        if results:
            rows = ""
            for s in results:
                scores_badges = "".join([f'<span class="badge bg-info bg-opacity-10 text-dark border me-1">{m}: {d}</span>' for m, d in s["scores"].items()]) or '<em>Chưa có điểm</em>'
                avg_disp = s["average"] if s["average"] is not None else "N/A"
                rows += f"""
                <tr>
                    <td class="ps-4"><span class="badge bg-secondary">{s["mssv"]}</span></td>
                    <td class="fw-semibold">{s["name"]}</td>
                    <td>{s["lop"]}</td>
                    <td>{scores_badges}</td>
                    <td class="fw-bold text-primary">{avg_disp}</td>
                    <td><span class="badge bg-primary">{s["rank"]}</span></td>
                </tr>
                """
            results_html = f"""
            <div class="content-box p-0 overflow-hidden">
                <div class="p-3 bg-light border-bottom">
                    <span class="text-muted">Kết quả tìm kiếm cho: </span><strong>"{html.escape(query)}"</strong> ({len(results)} kết quả)
                </div>
                <table class="table table-hover align-middle mb-0">
                    <thead class="table-light">
                        <tr>
                            <th class="ps-4">Mã SV</th>
                            <th>Họ và tên</th>
                            <th>Lớp</th>
                            <th>Điểm môn học</th>
                            <th>Điểm TB</th>
                            <th>Xếp loại</th>
                        </tr>
                    </thead>
                    <tbody>{rows}</tbody>
                </table>
            </div>
            """
        else:
            results_html = f'<div class="content-box text-center text-muted">Không tìm thấy sinh viên nào phù hợp với "{html.escape(query)}".</div>'

    body = f"""
    <div class="content-box mb-4">
        <h4 class="fw-bold mb-3">Tìm Kiếm Sinh Viên</h4>
        <form method="GET" action="{url_for('search')}" class="row g-2">
            <div class="col-md-10">
                <input type="text" name="q" class="form-control form-control-lg" placeholder="Nhập tên hoặc mã sinh viên..." value="{html.escape(query)}">
            </div>
            <div class="col-md-2">
                <button type="submit" class="btn btn-primary btn-lg w-100"><i class="bi bi-search me-1"></i>Tìm kiếm</button>
            </div>
        </form>
    </div>
    {results_html}
    """
    return layout("Tìm kiếm", body)

# -----------------------------------------------------------------------------
# RESTful API ENDPOINTS
# -----------------------------------------------------------------------------
@app.route("/api/students", methods=["GET"])
def api_get_students():
    data = [student_summary(mssv) for mssv in STUDENTS.keys()]
    return jsonify({"success": True, "data": data, "total": len(data)})

@app.route("/api/students/<string:mssv>", methods=["GET"])
def api_get_student_detail(mssv):
    s = student_summary(mssv)
    if not s:
        return jsonify({"success": False, "message": "Không tìm thấy sinh viên"}), 404
    return jsonify({"success": True, "data": s})

# -----------------------------------------------------------------------------
# XỬ LÝ LỖI
# -----------------------------------------------------------------------------
@app.errorhandler(404)
def not_found_error(error):
    body = f"""
    <div class="text-center py-5">
        <h1 class="display-1 fw-bold text-danger">404</h1>
        <h3 class="fw-bold">Trang không tồn tại</h3>
        <p class="text-muted">Đường dẫn bạn truy cập không hợp lệ.</p>
        <a href="{url_for('home')}" class="btn btn-primary mt-3"><i class="bi bi-house me-1"></i>Trở về Trang chủ</a>
    </div>
    """
    return layout("Lỗi 404", body), 404

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)