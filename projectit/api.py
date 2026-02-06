import frappe
from datetime import date

@frappe.whitelist()
def get_employee_id(user_id):
    employee_id = frappe.get_list("Employee",filters={ 'user_id' : user_id},fields=["name"]) 
    if employee_id :
        return employee_id[0].name

@frappe.whitelist()
def get_session_user():
    user = frappe.session.user
    if user == "Guest":
        return None
    return user

@frappe.whitelist()
def get_current_projectit_user():
    user = frappe.session.user

    if user == "Guest":
        frappe.throw("Not logged in", frappe.PermissionError)

    employee = frappe.db.get_value(
        "Employee",
        {"user_id": user},
        ["name", "employee_name", "company"],
        as_dict=True
    )

    if not employee:
        return {
            "user": user,
            # "employee_id": "",
            # "employee_name": "",
            "company": "No Company",
        }

    return {
        "user": user,
        "employee_id": employee.name,
        "employee_name": employee.employee_name,
        "company": employee.company,
    }


#Функция для получения задач
@frappe.whitelist()
def get_employee_tasks(employee_id):
    current_user = frappe.session.user

    employee = frappe.get_value(
        "Employee",
        {"name": employee_id},
        ["name", "user_id"],
        as_dict=True
    )

    if not employee or employee.user_id != current_user:
        return []

    projects = frappe.db.sql("""
        SELECT pu.parent
        FROM `tabProject User` pu
        INNER JOIN `tabProject` p ON p.name = pu.parent
        WHERE pu.user = %(user)s
    """, {"user": current_user}, as_dict=True)

    if not projects:
        return current_user

    project_names = [p.parent for p in projects]

    tasks = frappe.db.sql("""
        SELECT
            t.name,
            t.subject,
            t.project,
            t.status,
            t.priority,
            t.exp_start_date,
            t.exp_end_date,
            t.description
        FROM `tabTask` t
        WHERE
            t.project IN %(projects)s
            AND t.custom_assigned_user = %(user)s
            AND t.status IN ('Open', 'Working')
    """, {
        "user": current_user,
        "projects": tuple(project_names),
    }, as_dict=True)

    return tasks

@frappe.whitelist()
def get_task_name(task):
    task = frappe.get_value(
        'Task',
        {"name": task},
        ["subject"]
    )
    return task.subject

@frappe.whitelist()
def update_task_status(task_id: str, status: str, completed_on: str):
    if not frappe.db.exists("Task", task_id):
        frappe.throw(f"Task {task_id} not found")

    if not completed_on:
        completed_on = ''

    task = frappe.get_doc("Task", task_id)
    task.status = status
    task.completed_on = completed_on
    task.save(ignore_permissions=True)

    frappe.db.commit()

    return {
        "task": task_id,
        "status": status,
        "completed_on": completed_on
    }

import frappe

@frappe.whitelist()
def add_task_to_history(task: str):
    """
    Добавляет выполненную задачу в Task List History
    """

    if not task:
        frappe.throw("Task is required")

    user = frappe.session.user

    # Проверяем, существует ли уже запись (чтобы не дублировать)
    exists = frappe.db.exists(
        "Task List History",
        {
            "task": task,
            "user": user
        }
    )

    if exists:
        return {
            "status": "exists",
            "message": "Task already in history"
        }

    task_doc = frappe.get_doc("Task", task)

    doc = frappe.get_doc({
        "doctype": "Task List History",
        "task": task_doc.name,
        "project": task_doc.project,
        "user": user
    })

    doc.insert(ignore_permissions=True)

    return {
        "status": "success",
        "name": doc.name
    }


@frappe.whitelist()
def get_project_allocation(user_company):
    if frappe.has_permission("Project", ptype="read"):
        if isinstance(user_company, str):
            user_company = [user_company]

        project_list = frappe.db.sql("""
            SELECT
                p.name,
                p.project_name,
                p.custom_project_manager
            FROM `tabProject` p
            WHERE
                p.company IN %(user_company)s
                AND EXISTS (
                    SELECT 1
                    FROM `tabProject User` pu
                    WHERE pu.parent = p.name
                      AND pu.user = %(user)s
                )
        """, {
            "user_company": tuple(user_company), 
            "user": frappe.session.user
        }, as_dict=True)
        return project_list
    else:
        return []



@frappe.whitelist()
def upload_base64_file(content, filename, dt=None, dn=None, fieldname=None):
    import base64
    import io
    from mimetypes import guess_type

    from PIL import Image, ImageOps

    from frappe.handler import ALLOWED_MIMETYPES

    decoded_content = base64.b64decode(content)
    content_type = guess_type(filename)[0]
    if content_type not in ALLOWED_MIMETYPES:
        frappe.throw(_("You can only upload JPG, PNG, PDF, TXT or Microsoft documents."))

    if content_type.startswith("image/jpeg"):
        # transpose the image according to the orientation tag, and remove the orientation data
        with Image.open(io.BytesIO(decoded_content)) as image:
            transpose_img = ImageOps.exif_transpose(image)
            # convert the image back to bytes
            file_content = io.BytesIO()
            transpose_img.save(file_content, format="JPEG")
            file_content = file_content.getvalue()
    else:
        file_content = decoded_content

    return frappe.get_doc(
        {
            "doctype": "File",
            "attached_to_doctype": dt,
            "attached_to_name": dn,
            "attached_to_field": fieldname,
            "folder": "Home",
            "file_name": filename,
            "content": file_content,
            "is_private": 0,
        }
    ).insert()

@frappe.whitelist()
def get_work_time_settings():
    return frappe.get_single("Work Time Settings")

@frappe.whitelist(allow_guest = True)
def get_header_info():
    app_logo = frappe.get_single("Navbar Settings").app_logo
    company = frappe.get_single("Global Defaults").default_company
    return app_logo,company

@frappe.whitelist()
def get_instructions(project_name,employee_id):
    if frappe.has_permission("Project" ,ptype="read") :
        data = frappe.db.sql("""
            SELECT pai.work_instruction, eai.instructions
            FROM `tabProject Allocation and Instrucions` as pai
            LEFT JOIN `tabEmployee Allocation Instruction` as eai
                ON eai.employee =  %(employee)s and eai.parent = pai.name
            WHERE pai.project_name = %(project_name)s
            ORDER BY  eai.modified DESC
            LIMIT 1
            """,{"employee" : employee_id,"project_name" : project_name},as_dict=True)
        return data 
    else : 
        return []

@frappe.whitelist()
def get_team_members(project_name):
    if frappe.has_permission("Project" ,ptype="read") :
        data = frappe.db.sql("""
            select project_name,
            CONCAT('[',GROUP_CONCAT(JSON_OBJECT("employee_name",employee_name,"activity" , activity)),']') as members
            from(
                select eai.employee_name, pai.project_name, case when t.start_date then 'active' else 'inactive' end as activity
                from `tabProject Allocation and Instrucions` as pai
                left join `tabEmployee Allocation Instruction` as eai on eai.parent = pai.name
                left join `tabTimesheet` as t
                    on 
                        t.employee = eai.employee 
                        and t.parent_project = pai.project 
                        and t.start_date = %(today)s
                        and t.docstatus = 0
                where pai.project_name = %(project_name)s
                ) as ts
            
            """,{ "today" : date.today(),"project_name" : project_name},as_dict = True)

        return data
    else :
        return []
        
@frappe.whitelist()
def get_employee_schedule(date,employee_id):
    if frappe.has_permission("Project" ,ptype="read") :
        project_list = frappe.db.sql("""
            select pai.project_name
            from `tabEmployee Allocation Instruction` as  eai 
            left join `tabProject Allocation and Instrucions` as  pai on eai.parent = pai.name
            where eai.employee = %(employee_id)s 
            """,{"employee_id" : employee_id},as_dict = True)
    
        return project_list

    frappe.throw(msg = "You Don't have enough Permission",exc = PermissionError)


@frappe.whitelist()
def project_with_members(employee_id):
    employee_id = get_employee_id(frappe.session.user)
    if employee_id :
        modules = frappe.get_list("Mobile Module",
        parent_doctype = "Employee",
        fields = ["module_name"],
        filters={"parent" : employee_id},pluck="module_name")

        if "ManageIT" in modules : 
            data = frappe.db.sql("""
                select p.project_name,
                CONCAT('[',GROUP_CONCAT(JSON_OBJECT("employee_name",employee_name,"activity" , activity)),']') as members
                from(
                    select eai.employee_name, pai.project_name, case when t.start_date then 'active' else 'inactive' end as activity
                    from `tabProject Allocation and Instrucions` as pai 
                    right join `tabEmployee Allocation Instruction` as eai on eai.parent = pai.name
                    left join `tabTimesheet` as t
                        on 
                            t.employee = eai.employee 
                            and t.parent_project = pai.project 
                            and t.start_date = %(today)s
                            and t.docstatus = 0
                    ) as ts
                RIGHT JOIN tabProject as p ON p.project_name = ts.project_name
                WHERE p.status = 'Open'
                GROUP BY project_name
                
                """,{ "today" : date.today()},as_dict = True)

            return data

    frappe.throw(msg = "You Don't have enough Permission",exc = PermissionError)

@frappe.whitelist()
def get_project_list():
    project_list = frappe.get_list("Project",filters={"status" : 'Open'},fields=["project_name"])
    return project_list 

@frappe.whitelist()
def get_modules_for_router():
    user = frappe.session.user
    if user == "Guest":
        frappe.throw("Not permitted", frappe.PermissionError)

    employee_id = get_employee_id(user)

    modules = frappe.get_list(
        "Mobile Module",
        parent_doctype="Employee",
        filters={"parent": employee_id},
        pluck="module_name"
    )
    return [m.lower() for m in modules]


@frappe.whitelist()
def get_employee_with_workit(project_name):
    if frappe.has_permission("Employee" ,ptype="read") :
        employee = frappe.db.sql("""

            select mm.parent as name, e.employee_name
            from `tabMobile Module` as mm
            left join tabEmployee as e
                on mm.parent = e.name
            where module_name = "WorkIT"
            except
            select eai.employee as name, eai.employee_name
            from`tabProject Allocation and Instrucions` as pai
            left join `tabEmployee Allocation Instruction` as eai 
                on eai.parent = pai.name
            where  pai.project_name = %(project_name)s
            """,{"project_name" : project_name},as_dict=True)
        return employee
    else :
        return []