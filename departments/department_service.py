from departments.department_repository import DepartmentRepository


class DepartmentService :
    def __init__(self, dept_repo : DepartmentRepository):
        self.repo = dept_repo

    def display_dept_by_dept(self, name : str) :
        return self.repo.select_dept_by_dept(name)