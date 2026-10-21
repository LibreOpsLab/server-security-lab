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
    for name, group in (("staff", "lab-staff"), ("finance", "finance")):
        body = share(name)
        assert f"valid users = @{group}" in body
        assert not re.search(r"guest ok\s*=\s*yes", body)


def test_server_joins_the_domain_with_ads_security_and_winbind_ids():
    conf = smb_conf()
    assert "security = ads" in conf and "{{ lab_realm }}" in conf
    assert "idmap config {{ lab_netbios }} : backend = rid" in conf


def test_sftp_is_chrooted_for_the_staff_group():
    dropin = (ROLE / "templates/20-sftp.conf.j2").read_text()
    assert "Match Group lab-staff" in dropin and "ChrootDirectory {{ files_server_sftp_root }}/%u" in dropin
    assert "ForceCommand internal-sftp" in dropin
    assert "/srv/sftp" in (ROLE / "defaults/main.yml").read_text()


def test_join_does_not_put_the_admin_password_on_a_command_line():
    join = (LAB / "ansible/roles/domain_join/tasks/join.yml").read_text()
    assert "kinit" in join and "net ads join -k" in join and "-U Administrator%" not in join
    assert "domain_join" in (ROLE / "tasks/main.yml").read_text()  # files01 reuses the shared join steps


def test_files_play_is_part_of_the_services_playbook():
    assert "files_server" in (LAB / "ansible/playbooks/40-services.yml").read_text()


def test_valid_users_group_does_not_collide_with_a_standard_debian_local_group():
    # Debian/Ubuntu ship a local group literally named "staff" (gid 50); NSS order "files systemd winbind"
    # means a plain @staff reference resolves to that LOCAL group, never the AD one. Use a name that cannot
    # collide with any standard system group.
    conf = smb_conf()
    for group in re.findall(r"valid users = @(\S+)", conf):
        assert group not in {"staff", "adm", "sudo", "disk", "lp", "mail", "news", "uucp", "man", "dialout", "fax", "voice", "cdrom", "floppy", "tape", "audio", "dip", "video", "plugdev", "netdev", "users"}, group


def test_sftp_match_group_does_not_collide_either():
    group = re.search(r"Match Group (\S+)", (ROLE / "templates/20-sftp.conf.j2").read_text()).group(1)
    assert group != "staff"
