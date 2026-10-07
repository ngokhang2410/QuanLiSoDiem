# Báo cáo Kiểm thử và Vận hành Ứng dụng Sổ điểm

## 1. Danh sách Route (`flask --app sodiem routes`)

```text
Endpoint                  Methods  Rule
------------------------  -------  -----------------------------------------
api_student_course_score  DELETE, GET, POST, PUT /api/students/<mssv>/scores/<course>
api_student_detail        GET      /api/students/<mssv>
api_students              GET      /api/students
export_csv                GET      /students/<mssv>/export
index                     GET      /
search                    GET      /search
short_detail              GET      /sv/<mssv>
static                    GET      /static/<path:filename>
student_detail            GET      /students/<mssv>
student_list              GET      /students