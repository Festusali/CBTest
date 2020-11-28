"""Defines set of utility functions and classes."""

def u_p_path(instance, filename):
    """Compute path where profile picture will be saved."""

    return f"images/user_pictures/{instance.user}.{filename.split('.')[-1]}"


def u_s_path(instance, filename):
    """Compute path where signature image will be saved."""

    return f"images/user_signatures/{instance.user}.{filename.split('.')[-1]}"
