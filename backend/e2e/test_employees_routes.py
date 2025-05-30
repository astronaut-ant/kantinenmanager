"""End-to-End tests for the employees routes."""

import uuid
from .helper import *  # for fixtures # noqa: F403
from .helper import login
from src.models.employee import Employee
from io import BytesIO


def describe_employees():
    def describe_get():
        def it_returns_all_employees_for_verwaltung(
            client, user_verwaltung, employees, group, location, db
        ):
            db.session.add(user_verwaltung)
            db.session.add(location)
            db.session.add(group)
            db.session.add_all(employees)
            db.session.commit()
            login(user=user_verwaltung, client=client)

            res = client.get("/api/employees")

            assert res.status_code == 200
            assert len(res.json) == len(employees)

        def it_returns_employees_filtered_by_first_name(
            client, user_verwaltung, employees, group, location, db
        ):
            db.session.add(user_verwaltung)
            db.session.add(location)
            db.session.add(group)
            db.session.add_all(employees)
            db.session.commit()
            login(user=user_verwaltung, client=client)

            res = client.get(f"/api/employees?first_name={employees[0].first_name}")

            assert res.status_code == 200
            assert len(res.json) == 1
            assert res.json[0]["first_name"] == employees[0].first_name

        def it_returns_employees_filtered_by_last_name(
            client, user_verwaltung, employees, group, location, db
        ):
            db.session.add(user_verwaltung)
            db.session.add(location)
            db.session.add(group)
            db.session.add_all(employees)
            db.session.commit()
            login(user=user_verwaltung, client=client)

            res = client.get(f"/api/employees?last_name={employees[0].last_name}")

            assert res.status_code == 200
            assert len(res.json) == 1
            assert res.json[0]["last_name"] == employees[0].last_name

        def it_returns_employees_filtered_by_employee_number(
            client, user_verwaltung, employees, group, location, db
        ):
            db.session.add(user_verwaltung)
            db.session.add(location)
            db.session.add(group)
            db.session.add_all(employees)
            db.session.commit()
            login(user=user_verwaltung, client=client)

            res = client.get(
                f"/api/employees?employee_number={employees[0].employee_number}"
            )

            assert res.status_code == 200
            assert len(res.json) == 1
            assert res.json[0]["employee_number"] == employees[0].employee_number

        def it_returns_employees_filtered_by_group_name(
            client, user_verwaltung, employees, group, location, db
        ):
            db.session.add(user_verwaltung)
            db.session.add(location)
            db.session.add(group)
            db.session.add_all(employees)
            db.session.commit()
            login(user=user_verwaltung, client=client)

            res = client.get(f"/api/employees?group_name={group.group_name}")

            assert res.status_code == 200
            assert len(res.json) == len(employees)

        def it_returns_employees_for_standortleitung_at_their_location(
            client, user_standortleitung, employees, group, location, db
        ):
            user_standortleitung.location_id = location.id
            db.session.add(user_standortleitung)
            db.session.add(location)
            db.session.add(group)
            db.session.add_all(employees)
            db.session.commit()
            login(user=user_standortleitung, client=client)

            res = client.get("/api/employees")

            assert res.status_code == 200
            assert len(res.json) == len(employees)

        def it_does_not_return_employees_from_different_location_for_standortleitung(
            client,
            user_standortleitung,
            employees,
            group,
            other_group,
            location,
            other_location,
            db,
        ):
            # Setup the original location and employees
            user_standortleitung.location_id = location.id
            db.session.add(user_standortleitung)
            db.session.add(location)
            db.session.add(group)
            db.session.add_all(employees)
            db.session.add(other_location)
            db.session.add(other_group)

            other_employee = Employee(
                first_name="Other",
                last_name="Employee",
                employee_number=9999,
                group_id=other_group.id,
            )
            other_employee.id = uuid.uuid4()
            db.session.add(other_employee)

            db.session.commit()
            login(user=user_standortleitung, client=client)

            res = client.get("/api/employees")

            assert res.status_code == 200
            assert len(res.json) == len(
                employees
            )  # Only employees from the leader's location
            employee_ids = [emp["id"] for emp in res.json]
            assert str(other_employee.id) not in employee_ids

        def it_returns_employees_for_gruppenleitung_of_their_group(
            client, user_gruppenleitung, employees, group, location, db
        ):
            db.session.add(user_gruppenleitung)
            db.session.add(location)
            db.session.add(group)
            db.session.add_all(employees)
            db.session.commit()
            login(user=user_gruppenleitung, client=client)

            res = client.get("/api/employees")

            assert res.status_code == 200
            assert len(res.json) == len(employees)

        def it_returns_employees_from_multiple_groups_for_gruppenleitung_as_leader_and_replacement(
            client, user_gruppenleitung, group, other_group, location, db
        ):
            # Set up the original group with user_gruppenleitung as leader
            other_group.location_id = location.id
            other_group.user_id_replacement = group.user_id_group_leader
            db.session.add(user_gruppenleitung)
            db.session.add(location)
            db.session.add(group)
            db.session.add(other_group)

            # Create employees for the first group
            group_employees = []
            for x in range(3):
                employee = Employee(
                    first_name=f"GroupLeader{x}",
                    last_name=f"Employee{x}",
                    employee_number=100 + x,
                    group_id=group.id,
                )
                employee.id = uuid.uuid4()
                group_employees.append(employee)

            db.session.add_all(group_employees)

            # Create employees for the second group
            replacement_employees = []
            for x in range(2):
                employee = Employee(
                    first_name=f"Replacement{x}",
                    last_name=f"Employee{x}",
                    employee_number=2000 + x,
                    group_id=other_group.id,
                )
                employee.id = uuid.uuid4()
                replacement_employees.append(employee)

            db.session.add_all(replacement_employees)
            db.session.commit()

            # Login as gruppenleitung
            login(user=user_gruppenleitung, client=client)

            # Get all employees
            res = client.get("/api/employees")

            # Verify response
            assert res.status_code == 200

            # Should see employees from both groups
            assert len(res.json) == len(group_employees) + len(replacement_employees)

            # Verify we can see employees from both groups by checking employee numbers
            employee_numbers = [emp["employee_number"] for emp in res.json]

            # Check if all employee numbers from both groups are in the result
            for emp in group_employees:
                assert emp.employee_number in employee_numbers

            for emp in replacement_employees:
                assert emp.employee_number in employee_numbers

            # Check if we can filter by group name to get just one group's employees
            res_group1 = client.get(f"/api/employees?group_name={group.group_name}")
            assert res_group1.status_code == 200
            assert len(res_group1.json) == len(group_employees)

            res_group2 = client.get(
                f"/api/employees?group_name={other_group.group_name}"
            )
            assert res_group2.status_code == 200
            assert len(res_group2.json) == len(replacement_employees)

        def it_does_not_return_employees_from_different_group_for_gruppenleitung(
            client, user_gruppenleitung, employees, group, other_group, location, db
        ):
            # Setup the original group and employees
            group.user_id_group_leader = user_gruppenleitung.id
            db.session.add(user_gruppenleitung)
            db.session.add(location)
            db.session.add(group)
            db.session.add_all(employees)
            db.session.add(other_group)

            other_employee = Employee(
                first_name="Other",
                last_name="Employee",
                employee_number=9999,
                group_id=other_group.id,
            )
            other_employee.id = uuid.uuid4()
            db.session.add(other_employee)

            db.session.commit()
            login(user=user_gruppenleitung, client=client)

            res = client.get("/api/employees")

            assert res.status_code == 200
            assert len(res.json) == len(
                employees
            )  # Only employees from the leader's group
            employee_ids = [emp["id"] for emp in res.json]
            assert str(other_employee.id) not in employee_ids

        def it_returns_employees_for_kuechenpersonal_at_their_location(
            client, user_kuechenpersonal, employees, group, location, db
        ):
            user_kuechenpersonal.location_id = location.id
            db.session.add(user_kuechenpersonal)
            db.session.add(location)
            db.session.add(group)
            db.session.add_all(employees)
            db.session.commit()
            login(user=user_kuechenpersonal, client=client)

            res = client.get("/api/employees")

            assert res.status_code == 200
            assert len(res.json) == len(employees)

        def it_does_not_return_employees_from_different_location_for_kuechenpersonal(
            client,
            user_kuechenpersonal,
            employees,
            group,
            other_group,
            location,
            other_location,
            db,
        ):
            # Setup the original location and employees
            user_kuechenpersonal.location_id = location.id
            db.session.add(user_kuechenpersonal)
            db.session.add(location)
            db.session.add(group)
            db.session.add_all(employees)
            db.session.add(other_location)
            db.session.add(other_group)

            other_employee = Employee(
                first_name="Other",
                last_name="Employee",
                employee_number=9999,
                group_id=other_group.id,
            )
            other_employee.id = uuid.uuid4()
            db.session.add(other_employee)

            db.session.commit()
            login(user=user_kuechenpersonal, client=client)

            res = client.get("/api/employees")

            assert res.status_code == 200
            assert len(res.json) == len(employees)  # Only employees from their location
            employee_ids = [emp["id"] for emp in res.json]
            assert str(other_employee.id) not in employee_ids

        def it_blocks_unauthenticated_users(client):
            res = client.get("/api/employees")

            assert res.status_code == 401

    def describe_get_by_id():
        def it_returns_employee_by_id_for_verwaltung(
            client, user_verwaltung, employees, group, location, db
        ):
            db.session.add(user_verwaltung)
            db.session.add(location)
            db.session.add(group)
            db.session.add_all(employees)
            db.session.commit()
            login(user=user_verwaltung, client=client)

            res = client.get(f"/api/employees/{employees[0].id}")

            assert res.status_code == 200
            assert res.json["id"] == str(employees[0].id)
            assert res.json["first_name"] == employees[0].first_name
            assert res.json["last_name"] == employees[0].last_name

        def it_returns_404_if_employee_does_not_exist(client, user_verwaltung, db):
            db.session.add(user_verwaltung)
            db.session.commit()
            login(user=user_verwaltung, client=client)

            res = client.get(f"/api/employees/{uuid.uuid4()}")

            assert res.status_code == 404

        def it_returns_employee_for_standortleitung_at_their_location(
            client, user_standortleitung, employees, group, location, db
        ):
            user_standortleitung.location_id = location.id
            db.session.add(user_standortleitung)
            db.session.add(location)
            db.session.add(group)
            db.session.add_all(employees)
            db.session.commit()
            login(user=user_standortleitung, client=client)

            res = client.get(f"/api/employees/{employees[0].id}")

            assert res.status_code == 200
            assert res.json["id"] == str(employees[0].id)

        def it_returns_employee_for_gruppenleitung_in_their_group(
            client, user_gruppenleitung, employees, group, location, db
        ):
            db.session.add(user_gruppenleitung)
            db.session.add(location)
            db.session.add(group)
            db.session.add_all(employees)
            db.session.commit()
            login(user=user_gruppenleitung, client=client)

            res = client.get(f"/api/employees/{employees[0].id}")

            assert res.status_code == 200
            assert res.json["id"] == str(employees[0].id)
            assert res.json["first_name"] == employees[0].first_name
            assert res.json["last_name"] == employees[0].last_name

        def it_returns_404_for_employee_not_in_gruppenleitung_group(
            client, user_gruppenleitung, employees, group, other_group, location, db
        ):
            db.session.add(user_gruppenleitung)
            db.session.add(location)
            db.session.add(group)
            db.session.add_all(employees)
            db.session.add(other_group)

            other_employee = Employee(
                first_name="Other",
                last_name="Employee",
                employee_number=9999,
                group_id=other_group.id,
            )
            other_employee.id = uuid.uuid4()
            db.session.add(other_employee)

            db.session.commit()
            login(user=user_gruppenleitung, client=client)

            res = client.get(f"/api/employees/{other_employee.id}")

            assert res.status_code == 404

        def it_returns_employee_for_kuechenpersonal_at_their_location(
            client, user_kuechenpersonal, employees, group, location, db
        ):
            user_kuechenpersonal.location_id = location.id
            db.session.add(user_kuechenpersonal)
            db.session.add(location)
            db.session.add(group)
            db.session.add_all(employees)
            db.session.commit()
            login(user=user_kuechenpersonal, client=client)

            res = client.get(f"/api/employees/{employees[0].id}")

            assert res.status_code == 200
            assert res.json["id"] == str(employees[0].id)
            assert res.json["first_name"] == employees[0].first_name
            assert res.json["last_name"] == employees[0].last_name

        def it_returns_404_for_employee_not_in_kuechenpersonal_location(
            client,
            user_kuechenpersonal,
            employees,
            group,
            other_group,
            location,
            other_location,
            db,
        ):
            user_kuechenpersonal.location_id = location.id
            db.session.add(user_kuechenpersonal)
            db.session.add(location)
            db.session.add(group)
            db.session.add_all(employees)
            db.session.add(other_location)
            db.session.add(other_group)

            other_employee = Employee(
                first_name="Other",
                last_name="Employee",
                employee_number=9999,
                group_id=other_group.id,
            )
            other_employee.id = uuid.uuid4()
            db.session.add(other_employee)

            db.session.commit()
            login(user=user_kuechenpersonal, client=client)

            res = client.get(f"/api/employees/{other_employee.id}")

            assert res.status_code == 404

    def describe_post():
        def it_creates_employee_for_verwaltung(
            client, user_verwaltung, group, location, db
        ):
            db.session.add(user_verwaltung)
            db.session.add(location)
            db.session.add(group)
            db.session.commit()
            login(user=user_verwaltung, client=client)

            body = {
                "first_name": "John",
                "last_name": "Doe",
                "employee_number": 12345,
                "group_name": group.group_name,
                "location_name": location.location_name,
            }

            res = client.post("/api/employees", json=body)

            assert res.status_code == 200
            assert "id" in res.json

            # Verify employee was created
            employees = db.session.query(Employee).all()
            assert len(employees) == 1
            assert employees[0].first_name == "John"
            assert employees[0].last_name == "Doe"
            assert employees[0].employee_number == 12345

        def it_returns_400_for_missing_fields(client, user_verwaltung, db):
            db.session.add(user_verwaltung)
            db.session.commit()
            login(user=user_verwaltung, client=client)

            res = client.post("/api/employees", json={})

            assert res.status_code == 400

        def it_checks_for_duplicate_employee_number(
            client, user_verwaltung, employees, group, location, db
        ):
            db.session.add(user_verwaltung)
            db.session.add(location)
            db.session.add(group)
            db.session.add_all(employees)
            db.session.commit()
            login(user=user_verwaltung, client=client)

            body = {
                "first_name": "John",
                "last_name": "Doe",
                "employee_number": employees[
                    0
                ].employee_number,  # Use existing employee number
                "group_name": group.group_name,
                "location_name": location.location_name,
            }

            res = client.post("/api/employees", json=body)

            assert res.status_code == 409

        def it_checks_if_group_exists(client, user_verwaltung, location, db):
            db.session.add(user_verwaltung)
            db.session.add(location)
            db.session.commit()
            login(user=user_verwaltung, client=client)

            body = {
                "first_name": "John",
                "last_name": "Doe",
                "employee_number": 12345,
                "group_name": "Non-Existent Group",
                "location_name": location.location_name,
            }

            res = client.post("/api/employees", json=body)

            assert res.status_code == 404

        def it_blocks_non_verwaltung_users(
            client, user_standortleitung, group, location, db
        ):
            db.session.add(user_standortleitung)
            db.session.add(location)
            db.session.add(group)
            db.session.commit()
            login(user=user_standortleitung, client=client)

            body = {
                "first_name": "John",
                "last_name": "Doe",
                "employee_number": 12345,
                "group_name": group.group_name,
                "location_name": location.location_name,
            }

            res = client.post("/api/employees", json=body)

            assert res.status_code == 403

    def describe_csv_create():
        def it_creates_employees_from_csv(client, user_verwaltung, group, location, db):
            db.session.add(user_verwaltung)
            db.session.add(location)
            db.session.add(group)
            db.session.commit()
            login(user=user_verwaltung, client=client)

            # Create a CSV file in memory
            csv_content = (
                "Kunden-Nr.,Kürzel,Bereich,Gruppe-Nr.,Gruppen-Name 1,Gruppen-Name 2\n"
            )
            csv_content += (
                f"9001,MaxMustermann,{location.location_name},1,{group.group_name},Test"
            )

            res = client.post(
                "/api/employees_csv",
                data={"file": (BytesIO(csv_content.encode("utf-8")), "employees.csv")},
                content_type="multipart/form-data",
            )

            assert res.status_code == 200

            # Verify employees were created
            employees = db.session.query(Employee).all()
            assert len(employees) == 1

        def it_returns_400_for_missing_file(client, user_verwaltung, db):
            db.session.add(user_verwaltung)
            db.session.commit()
            login(user=user_verwaltung, client=client)

            res = client.post("/api/employees_csv")

            assert res.status_code == 400

        def it_returns_400_for_empty_filename(client, user_verwaltung, db):
            db.session.add(user_verwaltung)
            db.session.commit()
            login(user=user_verwaltung, client=client)

            res = client.post(
                "/api/employees_csv",
                data={"file": (BytesIO(), "")},
                content_type="multipart/form-data",
            )

            assert res.status_code == 400

        def it_returns_415_for_wrong_file_format(client, user_verwaltung, db):
            db.session.add(user_verwaltung)
            db.session.commit()
            login(user=user_verwaltung, client=client)

            res = client.post(
                "/api/employees_csv",
                data={"file": (BytesIO(b"not a csv"), "employees.txt")},
                content_type="multipart/form-data",
            )

            assert res.status_code == 415

        def it_blocks_non_verwaltung_users(client, user_standortleitung, db):
            db.session.add(user_standortleitung)
            db.session.commit()
            login(user=user_standortleitung, client=client)

            csv_content = (
                "Kunden-Nr.,Kürzel,Bereich,Gruppe-Nr.,Gruppen-Name 1,Gruppen-Name 2\n"
            )
            csv_content += "9001,Mustermann,Test Location,1,Test Group,Test"

            res = client.post(
                "/api/employees_csv",
                data={"file": (BytesIO(csv_content.encode("utf-8")), "employees.csv")},
                content_type="multipart/form-data",
            )

            assert res.status_code == 403

    def describe_put():
        def it_updates_employee_for_verwaltung(
            client, user_verwaltung, employees, group, location, db
        ):
            db.session.add(user_verwaltung)
            db.session.add(location)
            db.session.add(group)
            db.session.add_all(employees)
            db.session.commit()
            login(user=user_verwaltung, client=client)

            body = {
                "first_name": "Updated",
                "last_name": "Name",
                "employee_number": 9999,
                "group_name": group.group_name,
                "location_name": location.location_name,
            }

            res = client.put(f"/api/employees/{employees[0].id}", json=body)

            assert res.status_code == 200
            assert res.json["first_name"] == "Updated"
            assert res.json["last_name"] == "Name"
            assert res.json["employee_number"] == 9999

        def it_returns_404_if_employee_does_not_exist(client, user_verwaltung, db):
            db.session.add(user_verwaltung)
            db.session.commit()
            login(user=user_verwaltung, client=client)

            body = {
                "first_name": "John",
                "last_name": "Doe",
                "employee_number": 12345,
                "group_name": "Test Group",
                "location_name": "Test Location",
            }

            res = client.put(f"/api/employees/{uuid.uuid4()}", json=body)

            assert res.status_code == 404

        def it_checks_for_duplicate_employee_number(
            client, user_verwaltung, employees, group, location, db
        ):
            db.session.add(user_verwaltung)
            db.session.add(location)
            db.session.add(group)
            db.session.add_all(employees)
            db.session.commit()
            login(user=user_verwaltung, client=client)

            body = {
                "first_name": "Updated",
                "last_name": "Name",
                "employee_number": employees[
                    1
                ].employee_number,  # Use another employee's number
                "group_name": group.group_name,
                "location_name": location.location_name,
            }

            res = client.put(f"/api/employees/{employees[0].id}", json=body)

            assert res.status_code == 409

        def it_blocks_non_verwaltung_users(
            client, user_standortleitung, employees, group, location, db
        ):
            db.session.add(user_standortleitung)
            db.session.add(location)
            db.session.add(group)
            db.session.add_all(employees)
            db.session.commit()
            login(user=user_standortleitung, client=client)

            body = {
                "first_name": "Updated",
                "last_name": "Name",
                "employee_number": 9999,
                "group_name": group.group_name,
                "location_name": location.location_name,
            }

            res = client.put(f"/api/employees/{employees[0].id}", json=body)

            assert res.status_code == 403

    def describe_delete():
        def it_deletes_employee_for_verwaltung(
            client, user_verwaltung, employees, group, location, db
        ):
            db.session.add(user_verwaltung)
            db.session.add(location)
            db.session.add(group)
            db.session.add_all(employees)
            db.session.commit()
            login(user=user_verwaltung, client=client)

            res = client.delete(f"/api/employees/{employees[0].id}")

            assert res.status_code == 200

            # Verify employee is hidden (soft-deleted)
            db_employees = db.session.query(Employee).all()
            assert len(db_employees) == len(employees) - 1

        def it_returns_404_if_employee_does_not_exist(client, user_verwaltung, db):
            db.session.add(user_verwaltung)
            db.session.commit()
            login(user=user_verwaltung, client=client)

            res = client.delete(f"/api/employees/{uuid.uuid4()}")

            assert res.status_code == 404

        def it_blocks_non_verwaltung_users(
            client, user_standortleitung, employees, group, location, db
        ):
            db.session.add(user_standortleitung)
            db.session.add(location)
            db.session.add(group)
            db.session.add_all(employees)
            db.session.commit()
            login(user=user_standortleitung, client=client)

            res = client.delete(f"/api/employees/{employees[0].id}")

            assert res.status_code == 403

    def describe_delete_list():
        def it_deletes_list_of_employees_for_verwaltung(
            client, user_verwaltung, employees, group, location, db
        ):
            db.session.add(user_verwaltung)
            db.session.add(location)
            db.session.add(group)
            db.session.add_all(employees)
            db.session.commit()
            login(user=user_verwaltung, client=client)

            employee_ids = [employees[0].id, employees[1].id]
            res = client.delete("/api/employees/", json={"employee_ids": employee_ids})

            assert res.status_code == 200

            db_employees = db.session.query(Employee).all()
            assert len(db_employees) == len(employees) - 2

        def it_returns_400_for_invalid_request_format(client, user_verwaltung, db):
            db.session.add(user_verwaltung)
            db.session.commit()
            login(user=user_verwaltung, client=client)

            res = client.delete("/api/employees/", json={"invalid": "format"})
            assert res.status_code == 400

            res = client.delete("/api/employees/", json={"employee_ids": "not-a-list"})
            assert res.status_code == 400

        def it_returns_404_if_any_employee_does_not_exist(
            client, user_verwaltung, employees, group, location, db
        ):
            db.session.add(user_verwaltung)
            db.session.add(location)
            db.session.add(group)
            db.session.add_all(employees)
            db.session.commit()
            login(user=user_verwaltung, client=client)

            employee_ids = [
                str(employees[0].id),
                str(uuid.uuid4()),
            ]  # One valid, one invalid
            res = client.delete("/api/employees/", json={"employee_ids": employee_ids})

            assert res.status_code == 404

    def describe_qr_codes():
        def it_returns_qr_codes_for_verwaltung(
            client, user_verwaltung, employees, group, location, db
        ):
            db.session.add(user_verwaltung)
            db.session.add(location)
            db.session.add(group)
            db.session.add_all(employees)
            db.session.commit()
            login(user=user_verwaltung, client=client)

            res = client.get("/api/employees/qr-codes")

            assert res.status_code == 200
            assert res.content_type == "application/pdf"

        def it_returns_qr_codes_for_standortleitung(
            client, user_standortleitung, employees, group, location, db
        ):
            user_standortleitung.location_id = location.id
            db.session.add(user_standortleitung)
            db.session.add(location)
            db.session.add(group)
            db.session.add_all(employees)
            db.session.commit()
            login(user=user_standortleitung, client=client)

            res = client.get("/api/employees/qr-codes")

            assert res.status_code == 200
            assert res.content_type == "application/pdf"

        def it_returns_qr_codes_for_gruppenleitung(
            client, user_gruppenleitung, employees, group, location, db
        ):
            db.session.add(user_gruppenleitung)
            db.session.add(location)
            db.session.add(group)
            db.session.add_all(employees)
            db.session.commit()
            login(user=user_gruppenleitung, client=client)

            res = client.get("/api/employees/qr-codes")

            assert res.status_code == 200
            assert res.content_type == "application/pdf"

        def it_blocks_kuechenpersonal(
            client, user_kuechenpersonal, employees, group, location, db
        ):
            user_kuechenpersonal.location_id = location.id
            db.session.add(user_kuechenpersonal)
            db.session.add(location)
            db.session.add(group)
            db.session.add_all(employees)
            db.session.commit()
            login(user=user_kuechenpersonal, client=client)

            res = client.get("/api/employees/qr-codes")

            assert res.status_code == 403

    def describe_qr_codes_by_list():
        def it_returns_qr_codes_for_specific_employees(
            client, user_verwaltung, employees, group, location, db
        ):
            db.session.add(user_verwaltung)
            db.session.add(location)
            db.session.add(group)
            db.session.add_all(employees)
            db.session.commit()
            login(user=user_verwaltung, client=client)

            employee_ids = [str(employees[0].id), str(employees[1].id)]
            res = client.post(
                "/api/employees/qr-codes-by-list", json={"employee_ids": employee_ids}
            )

            assert res.status_code == 200
            assert res.content_type == "application/pdf"

        def it_returns_400_for_invalid_request_format(client, user_verwaltung, db):
            db.session.add(user_verwaltung)
            db.session.commit()
            login(user=user_verwaltung, client=client)

            res = client.post(
                "/api/employees/qr-codes-by-list", json={"invalid": "format"}
            )
            assert res.status_code == 400

            res = client.post(
                "/api/employees/qr-codes-by-list", json={"employee_ids": "not-a-list"}
            )
            assert res.status_code == 400

        def it_returns_404_if_any_employee_does_not_exist(
            client, user_verwaltung, employees, group, location, db
        ):
            db.session.add(user_verwaltung)
            db.session.add(location)
            db.session.add(group)
            db.session.add_all(employees)
            db.session.commit()
            login(user=user_verwaltung, client=client)

            employee_ids = [
                str(employees[0].id),
                str(uuid.uuid4()),
            ]  # One valid, one invalid
            res = client.post(
                "/api/employees/qr-codes-by-list", json={"employee_ids": employee_ids}
            )

            assert res.status_code == 404
