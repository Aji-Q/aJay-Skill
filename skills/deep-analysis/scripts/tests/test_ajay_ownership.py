"""J Trader is the product brand; aJay ownership and legacy IDs stay intact."""
from __future__ import annotations

import importlib.util
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

ROOT = Path(__file__).resolve().parents[4]
SCRIPTS = ROOT / "skills/deep-analysis/scripts"
sys.path.insert(0, str(SCRIPTS))
CANONICAL = "Aji-Q/aJay-Skill"
VERSION = "1.2.0"


@pytest.mark.parametrize("relative", [
    ".claude-plugin/plugin.json", ".cursor-plugin/plugin.json",
    "package.json", "gemini-extension.json",
])
def test_distribution_metadata_has_one_current_version(relative):
    data = json.loads((ROOT / relative).read_text())
    assert data["name"] == "ajay"
    assert data["version"] == VERSION
    assert "J Trader" in data["description"]
    if "author" in data:
        author = data["author"]
        assert (author["name"] if isinstance(author, dict) else author) == "aJay"
    if "homepage" in data:
        assert data["homepage"] == f"https://github.com/{CANONICAL}"


@pytest.mark.parametrize("path", [ROOT / "SKILL.md", *sorted((ROOT / "skills").glob("*/SKILL.md"))])
def test_skill_author_is_current_maintainer_not_upstream(path):
    frontmatter = path.read_text().split("---", 2)[1]
    assert re.search(r"^author: aJay$", frontmatter, re.MULTILINE)
    assert re.search(rf"^version: {re.escape(VERSION)}$", frontmatter, re.MULTILINE)
    assert "license: MIT" in frontmatter


def test_marketplace_routes_to_ajay_plugin():
    data = json.loads((ROOT / ".claude-plugin/marketplace.json").read_text())
    assert data["name"] == "ajay-skill"
    assert data["owner"]["name"] == "aJay"
    assert data["plugins"][0]["name"] == "ajay"
    assert data["plugins"][0]["source"] == "./"


def test_product_brand_is_j_trader_while_legacy_ids_remain_compatible():
    package = json.loads((ROOT / "package.json").read_text())
    plugin = json.loads((ROOT / ".claude-plugin/plugin.json").read_text())
    marketplace = json.loads((ROOT / ".claude-plugin/marketplace.json").read_text())
    assert package["name"] == plugin["name"] == "ajay"
    assert marketplace["name"] == "ajay-skill"
    assert plugin["displayName"] == marketplace["plugins"][0]["displayName"] == "J Trader"
    assert "/ajay:" in (ROOT / "README.md").read_text()
    assert "AJAY_*" in (ROOT / "README.md").read_text()
    assert "J Trader 是产品名，aJay 是维护者" in (ROOT / "README.md").read_text()


@pytest.mark.parametrize("relative", [
    "README.md", "README_EN.md", ".codex/INSTALL.md", ".opencode/INSTALL.md",
    "GEMINI.md", "INSTALL-HERMES.md",
])
def test_active_install_docs_point_to_ajay_without_upstream_promotion(relative):
    content = (ROOT / relative).read_text()
    assert CANONICAL in content
    for stale in ("wbh604/UZI-Skill", "wbh604/jilao-skills", "Made by FloatFu", "wechat-group.jpg", "mmqrcode"):
        assert stale not in content


def test_copyright_and_provenance_are_preserved_not_claimed_exclusively():
    license_text = (ROOT / "LICENSE").read_text()
    assert "Copyright (c) 2026 Float Future" in license_text
    assert "Copyright (c) 2026 aJay (Aji-Q), for aJay-specific additions and modifications" in license_text
    assert "The above copyright notice and this permission notice shall be included" in license_text
    notice = (ROOT / "NOTICE").read_text()
    assert "wbh604/UZI-Skill" in notice
    assert "not transfer upstream copyright" in notice
    assert (ROOT / "docs/UPSTREAM-CONTRIBUTORS.md").is_file()
    assert (ROOT / "docs/archive/PRE-1.1.0-README.md").is_file()
    assert (ROOT / "docs/archive/PRE-1.1.0-README_EN.md").is_file()


def test_active_distribution_has_no_removed_contributor_manifest_links():
    assert not (ROOT / "CONTRIBUTORS.md").exists()
    assert "(CONTRIBUTORS.md)" not in (ROOT / "README.md").read_text()
    assert "(CONTRIBUTORS.md)" not in (ROOT / "README_EN.md").read_text()
    assert "See CONTRIBUTORS.md." not in (ROOT / "NOTICE").read_text()
    assert "(../CONTRIBUTORS.md)" not in (ROOT / "docs/OWNERSHIP.md").read_text()
    assert "contributors" not in json.loads((ROOT / "package.json").read_text())


def test_version_bump_manifest_tracks_current_files_including_root_skill_and_hook():
    data = json.loads((ROOT / ".version-bump.json").read_text())
    assert data["version"] == VERSION
    assert "SKILL.md" in data["files"]
    assert "hooks/session-start" in data["files"]
    for relative in data["files"]:
        assert (ROOT / relative).is_file()
        assert data["patterns"][relative].replace("VERSION", VERSION) in (ROOT / relative).read_text()


def test_update_checker_defaults_to_ajay_but_does_not_call_network_without_opt_in(monkeypatch):
    monkeypatch.delenv("AJAY_REPO", raising=False)
    spec = importlib.util.spec_from_file_location("ajay_identity_update_probe", SCRIPTS / "lib/update_check.py")
    module = importlib.util.module_from_spec(spec)
    # Dataclass inspects the defining module during initialization.
    monkeypatch.setitem(sys.modules, spec.name, module)
    spec.loader.exec_module(module)
    assert module.GITHUB_REPO == CANONICAL
    with patch("requests.get") as get:
        assert module._fetch_latest_release() is None
        get.assert_not_called()
    text = module.handle_answer("yes", VERSION)
    assert CANONICAL in text
    assert "wbh604" not in text
    assert "Hermes: git -C ~/aJay-Skill pull --ff-only" in text


def test_update_request_uses_explicit_ajay_destination(monkeypatch):
    from lib import update_check as uc
    monkeypatch.setenv("AJAY_REPO", CANONICAL)
    monkeypatch.setattr(uc, "GITHUB_REPO", CANONICAL)
    with patch("requests.get") as get:
        get.return_value.status_code = 404
        assert uc._fetch_latest_release() is None
    assert get.call_args.args[0] == f"https://api.github.com/repos/{CANONICAL}/releases/latest"


@pytest.mark.parametrize("filename", ["setup.sh", "install-hermes.sh"])
@pytest.mark.parametrize("remote,accepted", [
    ("https://github.com/Aji-Q/aJay-Skill.git", True),
    ("git@github.com:Aji-Q/aJay-Skill.git", True),
    ("https://github.com/wbh604/UZI-Skill.git", False),
])
def test_installers_verify_existing_origin_before_updates(tmp_path, filename, remote, accepted):
    if not shutil.which("git") or not shutil.which("bash"):
        pytest.skip("shell and git needed")
    subprocess.run(["git", "init", str(tmp_path)], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(tmp_path), "remote", "add", "origin", remote], check=True)
    content = (ROOT / filename).read_text()
    assert '${AJAY_REPO_URL:-https://github.com/Aji-Q/aJay-Skill.git}' in content
    start = content.index("normalize_repo_url()")
    end = content.index("\n}\n", content.index("verify_repo_origin()")) + len("\n}\n")
    helpers = content[start:end]
    script = helpers + f'\nREPO_URL="https://github.com/{CANONICAL}.git"\nverify_repo_origin "$1"'
    result = subprocess.run(["bash", "-c", script, "_", str(tmp_path)], capture_output=True, text=True)
    assert (result.returncode == 0) is accepted
    # Verification must not mutate any remote, even when rejecting a mismatch.
    actual = subprocess.check_output(["git", "-C", str(tmp_path), "remote", "get-url", "origin"], text=True).strip()
    assert actual == remote


def test_secondary_report_brand_and_disclaimer_belong_to_j_trader():
    for relative in ("lib/portfolio_runner.py", "lib/versus_runner.py"):
        content = (SCRIPTS / relative).read_text()
        assert "Generated by J Trader" in content
        assert f"J Trader v{VERSION}" in content
        assert "FloatFu-true" not in content
    disclaimer = (ROOT / "skills/deep-analysis/assets/disclaimer.md").read_text()
    assert "J Trader" in disclaimer
    assert "Maintained by aJay" in disclaimer
    assert "FloatFu-true" not in disclaimer


def test_session_hook_reports_current_j_trader_identity_without_network(monkeypatch):
    if not shutil.which("bash") or not shutil.which("python3"):
        pytest.skip("shell and python needed")
    monkeypatch.setenv("AJAY_NO_UPDATE_CHECK", "1")
    result = subprocess.run(["bash", str(ROOT / "hooks/session-start")], capture_output=True, text=True, check=True)
    context = json.loads(result.stdout)["additionalContext"]
    assert f"J Trader Research v{VERSION}" in context
    assert "aJay (Aji-Q)" in context
    assert "FloatFu-true" not in context


def test_update_cache_cannot_inherit_another_repository_release(tmp_path, monkeypatch):
    from lib import update_check as uc
    cache = tmp_path / "update.json"
    monkeypatch.setattr(uc, "_cache_path", lambda: cache)
    monkeypatch.setattr(uc, "GITHUB_REPO", CANONICAL)
    cache.write_text(json.dumps({"repository": "wbh604/UZI-Skill", "cached_latest": "9.9.9"}))
    assert uc._load_state() == {}
    uc._save_state({"cached_latest": "1.1.0"})
    assert uc._load_state()["repository"] == CANONICAL


def test_secondary_report_outputs_render_with_current_identity(tmp_path, monkeypatch):
    from lib import portfolio_runner, versus_runner
    # Identity test isolates the legacy CSS extraction from the primary UI build.
    (tmp_path / "report-template.html").write_text("<!doctype html><style>:root{--bg-card:white}</style>")
    monkeypatch.setattr(portfolio_runner, "ASSETS_DIR", tmp_path)
    monkeypatch.setattr(versus_runner, "ASSETS_DIR", tmp_path)
    stock = {"ticker": "AAPL", "name": "Fixture company", "industry": "Technology",
             "verdict": "Research only", "overall_score": 60, "_weight": 1.0}
    portfolio = portfolio_runner._render_html("Fixture portfolio", [stock], portfolio_runner._portfolio_health([stock]), "lite")
    versus = versus_runner._render_html([stock, {**stock, "ticker": "MSFT"}], "lite")
    for html in (portfolio, versus):
        assert "Generated by J Trader" in html
        assert f"J Trader v{VERSION}" in html
        assert "FloatFu-true" not in html
        assert "wbh604" not in html
