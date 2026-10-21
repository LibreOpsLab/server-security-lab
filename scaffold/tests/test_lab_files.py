import re
from pathlib import Path

LAB = Path(__file__).parents[2] / "lab"
ROLE = LAB / "ansible/roles/files_server"


def smb_conf():
    return (ROLE / "templates/smb.conf.j2").read_text()


def share(name):
    m = re.search(rf"^\[{name}\]\n(.*?)(?=^\[|\Z)", smb_conf(), re.S | re.M)
    assert m, f"no [{name}] share"
    return m.group(1)


def test_notices_share_is_guest_ok_and_the_server_maps_unknown_users_to_guest():
    assert re.search(r"^\s*guest ok\s*=\s*yes", share("notices"), re.M)
    assert re.search(r"^\s*map to guest\s*=\s*Bad User", smb_conf(), re.M)


def test_private_shares_are_restricted_to_their_group_and_not_guest_ok():
    for name, group in (("staff", "staff"), ("finance", "finance")):
        body = share(name)
        assert f"valid users = @{group}" in body
        assert not re.search(r"guest ok\s*=\s*yes", body)


def test_server_joins_the_domain_with_ads_security_and_winbind_ids():
    conf = smb_conf()
    assert "security = ads" in conf and "{{ lab_realm }}" in conf
    assert "idmap config {{ lab_netbios }} : backend = rid" in conf


def test_sftp_is_chrooted_for_the_staff_group():
    dropin = (ROLE / "templates/20-sftp.conf.j2").read_text()
    assert "Match Group staff" in dropin and "ChrootDirectory {{ files_server_sftp_root }}/%u" in dropin
    assert "ForceCommand internal-sftp" in dropin
    assert "/srv/sftp" in (ROLE / "defaults/main.yml").read_text()


def test_join_does_not_put_the_admin_password_on_a_command_line():
    tasks = (ROLE / "tasks/main.yml").read_text()
    assert "kinit" in tasks and "net ads join -k" in tasks and "-U Administrator%" not in tasks


def test_files_play_is_part_of_the_services_playbook():
    assert "files_server" in (LAB / "ansible/playbooks/40-services.yml").read_text()
