"""Non-UI activity query used by the shell's background expiry check."""


def account_operation_idle(robot_system) -> bool:
    manager = robot_system.system_manager
    if manager is not None and manager.active_process_id is not None:
        return False
    extensions = robot_system.account_access_extensions()
    check = extensions.activity_check or robot_system.get_account_access_change_block_reason
    return check() is None
