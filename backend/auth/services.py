"""Auth service facade — delegates to store (Postgres or in-memory)."""

from __future__ import annotations

from . import store

reset_registry = store.reset_registry
get_user_by_email = store.get_user_by_email
get_user_by_id = store.get_user_by_id
list_users = store.list_users
register_user = store.register_user
create_oauth_user = store.create_oauth_user
authenticate_user = store.authenticate_user
approve_user = store.approve_user
reject_user = store.reject_user
update_user_role = store.update_user_role
set_totp_secret = store.set_totp_secret
mark_2fa_enabled = store.mark_2fa_enabled
set_refresh_token_state = store.set_refresh_token_state
startup = store.startup
