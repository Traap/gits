import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import yaml
from typer.testing import CliRunner

from gits.main import app
from gits.utils.config_loader import load_repos
from gits.utils.operations import convert_repo, execute
from gits.utils.repos import filtered_repos


class RepositoryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.root = self.base / 'custom-root'
        self.config = self.base / 'repos.yml'
        self.write_config()
        patcher = patch('gits.utils.config_loader.CONFIG_FILE', self.config)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.runner = CliRunner()

    def write_config(self, **repo_options):
        self.config.write_text(yaml.safe_dump({'example': [
            {'root_dir': str(self.root)},
            {'repositories': [{'alias': 'repo', 'url': 'unused', **repo_options}]},
        ]}))

    def init_repo(self, path=None):
        path = path or self.root / 'repo'
        path.mkdir(parents=True)
        self.git(path, 'init')
        self.git(path, 'config', 'user.email', 'test@example.com')
        self.git(path, 'config', 'user.name', 'Test')
        (path / 'file').write_text('initial')
        self.git(path, 'add', 'file')
        self.git(path, 'commit', '-m', 'initial')
        return path

    def git(self, path, *args):
        return subprocess.run(['git', '-C', str(path), *args], check=True,
                              capture_output=True, text=True).stdout

    def test_paths_and_target_expansion(self):
        self.assertEqual(load_repos()[0].repositories[0].path, self.root / 'repo')
        self.write_config(target_path='~/elsewhere/repo')
        self.assertEqual(load_repos()[0].repositories[0].path, Path.home() / 'elsewhere/repo')

    def test_missing_root_defaults_to_home(self):
        self.config.write_text('example:\n  - repositories:\n      - alias: repo\n        url: unused\n')
        self.assertEqual(load_repos()[0].repositories[0].path, Path.home() / 'example/repo')

    def test_discovery_is_explicit_and_only_includes_git(self):
        self.init_repo()
        self.init_repo(self.root / 'extra')
        (self.root / 'ordinary').mkdir()
        self.assertEqual(len(load_repos()[0].repositories), 1)
        self.assertEqual(len(filtered_repos()), 1)
        self.assertEqual([r.alias for r in filtered_repos(include_unlisted=True)], ['repo', 'extra'])
        result = self.runner.invoke(app, ['clone', '-n'])
        self.assertEqual(result.exit_code, 0, result.output)

    def test_invalid_configuration_is_actionable(self):
        for content in ('', '[]', 'example: [null]', 'example: [{repositories: [null]}]'):
            self.config.write_text(content)
            result = self.runner.invoke(app, ['list'])
            self.assertNotEqual(result.exit_code, 0)
            self.assertIn('Invalid value', result.output)

    def test_unknown_group(self):
        result = self.runner.invoke(app, ['list', '-r', 'missing'])
        self.assertNotEqual(result.exit_code, 0)
        self.assertIn('Unknown repository group', result.output)

    def test_global_and_command_options(self):
        for args in (['-r', 'example', '-v', 'list'], ['list', '-r', 'example', '-v']):
            result = self.runner.invoke(app, args)
            self.assertEqual(result.exit_code, 0, result.output)
            self.assertIn('repo -> unused', result.output)
            self.assertNotIn('Not cloned', result.output)

    def test_default_status(self):
        result = self.runner.invoke(app, ['-r', 'example', '-v'])
        self.assertEqual(result.exit_code, 0, result.output)
        self.assertIn('Not cloned', result.output)

    def test_version_without_configuration(self):
        self.config.unlink()
        result = self.runner.invoke(app, ['version'])
        self.assertEqual(result.exit_code, 0, result.output)
        self.assertEqual(result.output, 'v0.3.0\n')

    def test_pop_dry_run_preserves_stash_and_worktree(self):
        path = self.init_repo()
        (path / 'file').write_text('stashed')
        self.git(path, 'stash')
        before = self.git(path, 'stash', 'list')
        for args in (['pop', '-n'], ['-n', 'pop']):
            result = self.runner.invoke(app, args)
            self.assertEqual(result.exit_code, 0, result.output)
            self.assertIn('dry-run', result.output)
            self.assertEqual(self.git(path, 'stash', 'list'), before)
            self.assertEqual((path / 'file').read_text(), 'initial')

    def test_git_failure_is_visible_without_verbose(self):
        self.init_repo()
        result = self.runner.invoke(app, ['pop'])
        self.assertEqual(result.exit_code, 1)
        self.assertIn('failed', result.output)
        self.assertIn('No stash entries', result.output)

    def test_convert_skips_directories_and_git_metadata(self):
        path = self.init_repo()
        (path / 'nested').mkdir()
        source = path / 'nested' / 'text'
        source.write_text('hello', encoding='utf-16')
        metadata = path / '.git' / 'keep'
        metadata.write_text('keep', encoding='utf-16')
        before = source.read_bytes()
        repo = filtered_repos()[0]
        convert_repo(repo, dry_run=True)
        self.assertEqual(source.read_bytes(), before)
        convert_repo(repo)
        self.assertEqual(source.read_bytes(), b'hello')
        self.assertTrue(metadata.read_bytes().startswith(b'\xff\xfe'))

    def test_worker_failures_are_collected(self):
        def broken(repo):
            raise OSError('worker failed')
        results = execute(filtered_repos(), broken, workers=4)
        self.assertEqual(results[0].state, 'failed')
        self.assertIn('worker failed', results[0].output)

    def test_delete_honors_root_protection_and_dry_run(self):
        path = self.init_repo()
        result = self.runner.invoke(app, ['delete', '-n'])
        self.assertEqual(result.exit_code, 0, result.output)
        self.assertTrue(path.exists())
        self.write_config(do_not_delete=True)
        result = self.runner.invoke(app, ['delete'])
        self.assertEqual(result.exit_code, 0, result.output)
        self.assertTrue(path.exists())
        self.write_config()
        result = self.runner.invoke(app, ['delete'])
        self.assertEqual(result.exit_code, 0, result.output)
        self.assertFalse(self.root.exists())

    def test_delete_preserves_unlisted_directories(self):
        self.init_repo()
        extra = self.root / 'extra'
        extra.mkdir()
        result = self.runner.invoke(app, ['delete'])
        self.assertEqual(result.exit_code, 0, result.output)
        self.assertTrue(extra.exists())

    def test_clone_and_pull_with_local_remote(self):
        remote = self.init_repo(self.base / 'remote')
        self.write_config(url=str(remote))
        result = self.runner.invoke(app, ['clone', '-n'])
        self.assertEqual(result.exit_code, 0, result.output)
        self.assertFalse(self.root.exists())
        result = self.runner.invoke(app, ['clone'])
        self.assertEqual(result.exit_code, 0, result.output)
        clone = self.root / 'repo'
        self.git(clone, 'config', 'user.email', 'test@example.com')
        self.git(clone, 'config', 'user.name', 'Test')
        (remote / 'new').write_text('upstream')
        self.git(remote, 'add', 'new')
        self.git(remote, 'commit', '-m', 'upstream')
        (clone / 'file').write_text('local changes')
        result = self.runner.invoke(app, ['pull', '-n'])
        self.assertEqual(result.exit_code, 0, result.output)
        self.assertFalse((clone / 'new').exists())
        self.assertEqual((clone / 'file').read_text(), 'local changes')
        result = self.runner.invoke(app, ['pull'])
        self.assertEqual(result.exit_code, 0, result.output)
        self.assertEqual((clone / 'new').read_text(), 'upstream')
        self.assertIn('WIP', self.git(clone, 'stash', 'list'))

    def test_delete_failure_is_reported(self):
        self.init_repo()
        with patch('gits.commands.delete.shutil.rmtree', side_effect=PermissionError('denied')):
            result = self.runner.invoke(app, ['delete'])
        self.assertEqual(result.exit_code, 1)
        self.assertIn('denied', result.output)
        self.assertTrue((self.root / 'repo').exists())

    def test_malformed_yaml_is_reported(self):
        self.config.write_text('example: [')
        result = self.runner.invoke(app, ['list'])
        self.assertNotEqual(result.exit_code, 0)
        self.assertIn('Invalid YAML', result.output)

    def test_clean_dry_run_and_execution(self):
        path = self.init_repo()
        (path / 'file').write_text('changed')
        extra = path / 'untracked'
        extra.write_text('untracked')
        result = self.runner.invoke(app, ['clean', '-n'])
        self.assertEqual(result.exit_code, 0, result.output)
        self.assertEqual((path / 'file').read_text(), 'changed')
        self.assertTrue(extra.exists())
        result = self.runner.invoke(app, ['clean'])
        self.assertEqual(result.exit_code, 0, result.output)
        self.assertEqual((path / 'file').read_text(), 'initial')
        self.assertFalse(extra.exists())


if __name__ == '__main__':
    unittest.main()
