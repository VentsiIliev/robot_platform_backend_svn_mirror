from src.applications.user_management.domain.user_schema import UserSchema, FieldDescriptor

# Safe presentation schema. Credentials are never part of a table/profile DTO.
DEFAULT_USER_SCHEMA = UserSchema(id_key="id", fields=[
    FieldDescriptor("id", "ID", "text"),
    FieldDescriptor("firstName", "First Name", "text"),
    FieldDescriptor("lastName", "Last Name", "text"),
    FieldDescriptor("role", "Role", "text"),
    FieldDescriptor("email", "Email", "text", required=False),
    FieldDescriptor("created_at", "Created at", "text", required=False),
    FieldDescriptor("created_by_label", "Created by", "text", required=False),
    FieldDescriptor("updated_at", "Edited at", "text", required=False),
    FieldDescriptor("updated_by_label", "Edited by", "text", required=False),
])

